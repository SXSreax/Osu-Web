from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
import os
import re
import zipfile
import requests
import shutil
import tempfile

from app.models import db, Beatmap, BeatmapDiff
from app.forms import UploadForm

upload_bp = Blueprint('upload', __name__)

CLIENT_ID = "49164"
CLIENT_SECRET = "Vh3zYLuWxYoRS7o2RmOvhEunh40Z8kWLfPw21tQm"

def fetch_star_rate(beatmapset_id: int, beatmap_id: int):
    token_res = requests.post(
        "https://osu.ppy.sh/oauth/token",
        json={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": "public"
        }
    )
    token = token_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}?mode=mania"
    response = requests.get(url, headers=headers)
    data = response.json()

    return data["difficulty_rating"]

def get_file_info(beatmap_path):
    map_name = os.path.basename(beatmap_path)
    beatmap_id = None
    beatmapset_id = None
    mode = None
    artist = None
    title = None

    try:
        try:
            with open(beatmap_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(beatmap_path, 'r', encoding='latin-1') as f:
                content = f.read()

        current_section = None
        lines = content.splitlines()
        version = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].lower()
                continue

            if current_section == 'general':
                if line.startswith('Mode:'):
                    m = re.match(r'Mode\s*:\s*(\d+)', line)
                    if m:
                        mode = int(m.group(1))

            if current_section == 'metadata':
                if line.startswith('Title:') and title is None:
                    m = re.match(r'Title\s*:\s*(.+)', line)
                    if m:
                        title = m.group(1).strip()
                
                elif line.startswith('Artist:') and artist is None:
                    m = re.match(r'Artist\s*:\s*(.+)', line)
                    if m:
                        artist = m.group(1).strip()

                elif line.startswith('Version:') and version is None:
                    m = re.match(r'Version\s*:\s*(.+)', line)
                    if m:
                        version = m.group(1).strip()

                elif line.startswith('BeatmapID:'):
                    m = re.match(r'BeatmapID\s*:\s*(\d+)', line)
                    if m:
                        beatmap_id = int(m.group(1))

                elif line.startswith('BeatmapSetID:'):
                    m = re.match(r'BeatmapSetID\s*:\s*(\d+)', line)
                    if m:
                        beatmapset_id = int(m.group(1))
                        
        if title:
            if version:
                map_name = f"{title} [{version}]"
            else:
                map_name = title

    except Exception as e:
        print(f"Error extracting IDs from {beatmap_path}: {e}")

    return map_name, beatmap_id, beatmapset_id, mode, artist, title

def sanitize_id(filename):
    name, ext = os.path.splitext(filename)
    match = re.match(r'^(\d+)', name)
    name = match.group(1)
    return name + ext.lower()

def sanitize_filename(filename):
    name, ext = os.path.splitext(filename)
    name = re.sub(r'[^\w\s\-\(\)]', '_', name)
    return name + ext

@upload_bp.route('/upload/')
@login_required
def upload():
    form = UploadForm()
    return render_template('pages/upload.html', form = form)

@upload_bp.route('/upload/store', methods=['POST'])
def upload_store():
    form = UploadForm()
    if not form.validate_on_submit():
        flash('Please upload a valid file', "error")
        return render_template('pages/upload.html', form=form)
    
    uploaded_file = form.file.data
    uploader = current_user.username

    if not uploaded_file or not (uploaded_file.filename.endswith('.osz') or uploaded_file.filename.endswith('.zip')):
        flash('Only accept .osz or .zip files.', "error")
        return redirect(url_for('upload.upload'))

    filename = secure_filename(uploaded_file.filename)
    
    with tempfile.TemporaryDirectory(dir=os.path.join(current_app.instance_path, 'temp_uploads')) as temp_dir:
        temp_zip_path = os.path.join(temp_dir, filename)
        uploaded_file.save(temp_zip_path)

        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except zipfile.BadZipFile:
            flash('The uploaded file is not a valid zip archive.', "error")
            return redirect(url_for('upload.upload'))

        osu_file_path = None
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.osu'):
                    osu_file_path = os.path.join(root, file)
                    break
            if osu_file_path:
                break
                
        if not osu_file_path:
            flash('The archive does not contain any .osu file.', "error")
            return redirect(url_for('upload.upload'))

        _, _, beatmapset_id, _, artist, title = get_file_info(osu_file_path)

        if not beatmapset_id or not artist or not title:
            flash('Could not extract necessary metadata (BeatmapSetID, Artist, Title) from the .osu file.', "error")
            return redirect(url_for('upload.upload'))

        maps_dir = os.path.join(current_app.instance_path, 'maps')
        os.makedirs(maps_dir, exist_ok=True)
        
        final_extract_folder = os.path.join(maps_dir, str(beatmapset_id))
        final_zip_path = os.path.join(maps_dir, str(beatmapset_id) + '.zip')

        if os.path.exists(final_extract_folder):
            shutil.rmtree(final_extract_folder)
    
        extracted_items = os.listdir(extract_dir)
        source_dir = extract_dir
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(extract_dir, extracted_items[0])):
            source_dir = os.path.join(extract_dir, extracted_items[0])
        
        shutil.copytree(source_dir, final_extract_folder)
        
        shutil.copy(temp_zip_path, final_zip_path) 

        relative_path = os.path.join('maps', str(beatmapset_id) + '.zip')
        
        existing = Beatmap.query.get(beatmapset_id)
        if existing:
            existing.name = title
            existing.artist = artist
            existing.uploader = uploader
            existing.filepath = relative_path
        else:
            beatmap = Beatmap(
                id=beatmapset_id,
                name=title,
                artist=artist,
                uploader=uploader,
                filepath=relative_path
            )
            db.session.add(beatmap)
        db.session.commit()

        try:
            osu_files = [f for f in os.listdir(final_extract_folder) if f.endswith('.osu')]
            mania_found = False
            for osu_file in osu_files:
                osu_path = os.path.join(final_extract_folder, osu_file)
                map_name_file, beatmap_id_file, beatmapset_id_file, mode_file, _, _ = get_file_info(osu_path)

                if mode_file != 3:
                    continue

                mania_found = True
                
                if beatmap_id_file and beatmapset_id_file:
                    star_rating = fetch_star_rate(beatmapset_id_file, beatmap_id_file)
                    star_truncated = int(star_rating * 100) / 100

                    existing_diff = BeatmapDiff.query.filter_by(
                        map_id=beatmapset_id_file,
                        map_name=map_name_file
                    ).first()

                    if existing_diff:
                        existing_diff.star_diff = star_truncated
                    else:
                        beatmap_diff = BeatmapDiff(
                            map_id=beatmapset_id_file,
                            map_name=map_name_file,
                            star_diff=star_truncated
                        )
                        db.session.add(beatmap_diff)
            
            db.session.commit()

        except Exception as e:
            print(f"Error fetching/storing star ratings: {e}")
            flash("Beatmap uploaded but failed to fetch mania star ratings.", "warning")
            return redirect(url_for('upload.upload'))

        if mania_found:
            flash('Beatmap updated successfully.', 'success')
        else:
            flash("This beatmapset contains no osu!mania maps.", "warning")
    
    return redirect(url_for('home.home'))

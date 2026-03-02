from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
import re
import zipfile
import requests

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

    try:
        try:
            with open(beatmap_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(beatmap_path, 'r', encoding='latin-1') as f:
                content = f.read()

        current_section = None
        lines = content.splitlines()
        title = None
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

    return map_name, beatmap_id, beatmapset_id, mode

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
def upload():
    form = UploadForm()
    return render_template('pages/upload.html', form = form)

@upload_bp.route('/upload/store', methods=['POST'])
def upload_store():
    form = UploadForm()
    if not form.validate_on_submit():
        flash('Please upload a valid file')
        return render_template('pages/upload.html', form=form)
    
    filenametemp = form.file.data
    uploader = form.uploader.data or 'anonymous'

    filename = sanitize_filename(filenametemp.filename)
    if not filename:
        flash('Invalid filename. File must be in (beatmapid - artist - name).osz/.zip')
        return redirect(url_for('upload.upload'))
    
    file_store_name = sanitize_id(filename)
    id_name = os.path.splitext(file_store_name)[0]
    
    fullname, extracted = os.path.splitext(filename)
    extracted = extracted.lower()

    maps_dir = os.path.join(current_app.instance_path, 'maps')
    os.makedirs(maps_dir, exist_ok=True)

    extract_folder = None
    if extracted == '.osz':
        stored_filename = id_name + '.zip'
        stored_path = os.path.join(maps_dir, stored_filename)
        filenametemp.save(stored_path)
        extract_folder = os.path.join(maps_dir, id_name)
        real_name = fullname + '.zip'
    elif extracted == '.zip':
        stored_filename = file_store_name
        stored_path = os.path.join(maps_dir, stored_filename)
        filenametemp.save(stored_path)
        extract_folder = os.path.join(maps_dir, id_name)
        real_name = filename
    else:
        flash('Only accept .osz or .zip files.')
        return redirect(url_for('upload.upload'))
    
    if extract_folder:
        os.makedirs(extract_folder, exist_ok=True)
        with zipfile.ZipFile(stored_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

    name_uncleaned = os.path.splitext(real_name)[0]
    name_cleaned = name_uncleaned.replace('_', ' ').strip()
    fetch_info = r'^(\d+)\s+(.+?)\s*-\s*(.+)$'
    same_match = re.match(fetch_info, name_cleaned)
    map_id = None
    artist = None
    name = None
    if same_match:
        map_id = int(same_match.group(1))
        artist = same_match.group(2).strip()
        name = same_match.group(3).strip()
    else:
        flash('Please ensure file name follows: beatmapid - artist - name')
        return redirect(url_for('upload.upload'))
    
    relative_path = os.path.join('maps', stored_filename)

    existing = Beatmap.query.get(map_id)
    if existing:
        existing.name = name or existing.name
        existing.artist = artist or existing.artist
        existing.uploader = uploader
        existing.filepath = relative_path
    else:
        beatmap = Beatmap(
            id=map_id,
            name=name,
            artist=artist,
            uploader=uploader,
            filepath=relative_path
        )
        db.session.add(beatmap)
    db.session.commit()

    try:
        osu_files = [f for f in os.listdir(extract_folder) if f.endswith('.osu')]
        mania_found = False
        for osu_file in osu_files:
            osu_path = os.path.join(extract_folder, osu_file)
            map_name_file, beatmap_id_file, beatmapset_id_file, mode_file = get_file_info(osu_path)

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

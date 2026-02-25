from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
import re
import zipfile
import time
#import requests

from app.models import db, Beatmap, BeatmapDiff
from app.forms import UploadForm

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload/')
def upload():
    form = UploadForm()
    return render_template('pages/upload.html', form = form)

@upload_bp.route('/upload/store', methods=['POST'])
def upload_store():
    form = UploadForm()
    if not form.validate_on_submit():
        flash('Please upload a vaild file')
        return render_template('pages/upload.html', form = form)
    
    filenametemp = form.file.data
    uploader = form.uploader.data or 'anonymous'

    filename = secure_filename(filenametemp.filename)
    if not filename:
        flash('Invaild filename. File must be in (beatmapid - artist - name).osz/.zip')
        return redirect(url_for('upload.upload'))
    
    fullname, extracted = os.path.splitext(filename)
    extracted = extracted.lower()

    maps_dir = os.path.join(current_app.instance_path,'maps')
    os.makedirs(maps_dir, exist_ok = True)

    extract_folder = None
    if extracted == '.osz':
        stored_filename = fullname + '.zip'
        stored_path = os.path.join(maps_dir, stored_filename)
        filenametemp.save(stored_path)
        extract_folder = os.path.join(maps_dir, fullname)
    elif extracted == '.zip':
        stored_filename = filename
        stored_path = os.path.join(maps_dir, stored_filename)
        filename.save(stored_path)
        extract_folder = os.path.join(maps_dir, os.path.splitext(stored_filename)[0])
    else:
        flash('Only except .osz or .zip files.')
        return redirect(url_for('upload.upload'))
    
    if extract_folder:
        os.makedirs(extract_folder, exist_ok=True)
        with zipfile.ZipFile(stored_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

    name_uncleaned = os.path.splitext(stored_filename)[0]
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
        db.session.commit()

        flash('Beatmap updated successfully.', 'success')
        return redirect(url_for('home.home'))

    beatmap = Beatmap(id=map_id,
                      name=name,
                      artist=artist,
                      uploader=uploader,
                      filepath=relative_path)
    db.session.add(beatmap)
    db.session.commit()

    flash('Beatmap updated successfully.', 'success')
    return redirect(url_for('home.home'))

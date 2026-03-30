from flask import Blueprint, render_template, current_app, send_file, flash, redirect, url_for, jsonify
from flask_login import current_user
import os
import random
import zipfile
import io
from app.models import db, Beatmap, BeatmapDiff, Favorite, User

map_bp = Blueprint('map', __name__)

@map_bp.route('/map/<int:beatmap_id>')
def map_detail(beatmap_id):
    bm = Beatmap.query.get_or_404(beatmap_id)
    
    maps_dir = os.path.join(current_app.instance_path, 'maps')
    base_name = os.path.splitext(os.path.basename(bm.filepath))[0]
    folder = os.path.join(maps_dir, base_name)
    
    cover_img = None
    if os.path.isdir(folder):
        imgs = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        if imgs:
            cover_img = os.path.join('maps', base_name, random.choice(imgs))

    user = User.query.get(bm.uploader)
    if user:
        uploader = user.username
    else:
        uploader = "anonymous"

    difficulties = BeatmapDiff.query.filter_by(map_id=bm.id).all()
    difficulty_list = []
    for d in difficulties:
        difficulty_dict = {
            'name': d.map_name,
            'star': d.star_diff
        }
        difficulty_list.append(difficulty_dict)

    favorited = False
    if current_user.is_authenticated:
        favorited = Favorite.query.filter_by(
            user_id=current_user.id,
            map_id=beatmap_id
        ).first() is not None

    return render_template('pages/map.html', bm={
        'id': bm.id,
        'name': bm.name,
        'artist': bm.artist,
        'uploader': uploader,
        'cover_img': cover_img,
        'filepath': bm.filepath,
        'difficulties': difficulty_list,
    }, favorited=favorited)

@map_bp.route('/map/download/<int:beatmap_id>/<format>')
def download_beatmap(beatmap_id, format):
    bm = Beatmap.query.get_or_404(beatmap_id)
    
    maps_dir = os.path.join(current_app.instance_path, 'maps')
    base_name = os.path.splitext(os.path.basename(bm.filepath))[0]
    folder = os.path.join(maps_dir, base_name)
    
    if not os.path.isdir(folder):
        return 'Beatmap folder not found', 404
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, folder))
    
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, 
                    download_name=f"{base_name}.{'osz' if format.lower() == 'osz' else 'zip'}")

@map_bp.route('/map/<int:beatmap_id>/favorite', methods=['POST'])
def favorite(beatmap_id):
    existing = Favorite.query.filter_by(user_id=current_user.id, map_id=beatmap_id).first()

    if existing:
        db.session.delete(existing)
        status = "removed"
    else:
        db.session.add(Favorite(user_id=current_user.id, map_id=beatmap_id))
        status = "added"

    db.session.commit()
    return jsonify({"status": status})

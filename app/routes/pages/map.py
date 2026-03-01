from flask import Blueprint, render_template, current_app, send_file
import os
import random
import zipfile
import io
from app.models import Beatmap, BeatmapDiff

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

    difficulties = BeatmapDiff.query.filter_by(map_id=bm.id).all()
    difficulty_list = []
    for d in difficulties:
        difficulty_dict = {
            'name': d.map_name,
            'star': d.star_diff
        }
        difficulty_list.append(difficulty_dict)

    return render_template('pages/map.html', bm={
        'id': bm.id,
        'name': bm.name,
        'artist': bm.artist,
        'uploader': bm.uploader,
        'cover_img': cover_img,
        'filepath': bm.filepath,
        'difficulties': difficulty_list,
    })

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
from flask import Blueprint, render_template, send_file, jsonify, current_app
from app.models import Beatmap, BeatmapDiff
import os
import random
import zipfile

beatmaps_bp = Blueprint('beatmaps', __name__)

@beatmaps_bp.route('/beatmaps/')
def beatmaps():
    maps = Beatmap.query.all()
    beatmap_card = []
    for bms in maps:
        maps_dir = os.path.join(current_app.instance_path, 'maps')
        map_name = os.path.splitext(os.path.basename(bms.filepath))[0]
        folder = os.path.join(maps_dir, map_name)
        cover_img = None
        
        if os.path.isdir(folder):
            imgs = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            if imgs:
                cover_img = os.path.join('maps', map_name, random.choice(imgs))

        beatmap_card.append({
                'id': bms.id,
                'name': bms.name,
                'artist': bms.artist,
                'uploader': bms.uploader,
                'cover_img': cover_img,
            })
    return render_template('pages/beatmaps.html', beatmaps=beatmap_card)


@beatmaps_bp.route('/instance/<path:filepath>')
def serve_instance_file(filepath):
    instance_path = current_app.instance_path
    file_path = os.path.join(instance_path, filepath)
    if not os.path.abspath(file_path).startswith(os.path.abspath(instance_path)):
        return 'Forbidden', 403
    if os.path.isfile(file_path):
        return send_file(file_path)
    return 'Not Found', 404
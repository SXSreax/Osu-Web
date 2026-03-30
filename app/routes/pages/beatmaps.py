from flask import Blueprint, render_template, send_file, jsonify, current_app
from app.models import Beatmap, BeatmapDiff, User
from app.utils.files import serve_instance_file
import os
import random
import zipfile
from urllib.parse import quote

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

        user = User.query.get(bms.uploader)
        if user:
            uploader = user.username
        else:
            uploader = "anonymous"
        print(uploader)

        difficulties = BeatmapDiff.query.filter_by(map_id=bms.id).all()
        difficulty_list = []
        for d in difficulties:
            difficulty_dict = {
                'name': d.map_name,
                'star': d.star_diff
            }
            difficulty_list.append(difficulty_dict)

        beatmap_card.append({
                'id': bms.id,
                'name': bms.name,
                'artist': bms.artist,
                'uploader': uploader,
                'cover_img': cover_img,
                'difficulties': difficulty_list
            })
    return render_template('pages/beatmaps.html', beatmaps=beatmap_card)


@beatmaps_bp.route('/instance/<path:filepath>')
def instance(filepath):
    return serve_instance_file(filepath)

@beatmaps_bp.route('/get-beatmap-audio/<int:beatmap_id>')
def get_beatmap_audio(beatmap_id):
    
    bms = Beatmap.query.get(beatmap_id)
    if not bms:
        return jsonify({'error': 'Beatmap not found'}), 404

    maps_dir = os.path.join(current_app.instance_path, 'maps')
    base_name = os.path.splitext(os.path.basename(bms.filepath))[0]
    folder = os.path.join(maps_dir, base_name)

    if not os.path.isdir(folder):
        return jsonify({'error': 'No audio folder found'}), 404

    audio_extensions = ('.mp3', '.ogg', '.m4a', '.flac', '.wav', '.aac', '.wma')

    candidates = []
    for f in os.listdir(folder):
        full_path = os.path.join(folder, f)
        if not os.path.isfile(full_path):
            continue

        if f.lower().endswith(audio_extensions):
            if not f.lower().endswith('.wav'):
                candidates.append(f)

    if not candidates:
        return jsonify({'error': 'No audio file found'}), 404

    candidates.sort()
    audio_file = candidates[0]

    if audio_file:
        audio_url = f"/instance/maps/{base_name}/{quote(audio_file)}"
        print(f"Returning URL: {audio_url}")
        return jsonify({'audio_url': audio_url})

    return jsonify({'error': 'Could not select audio file'}), 404

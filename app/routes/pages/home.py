from flask import Blueprint, render_template, current_app
from sqlalchemy.sql.expression import func
from app.models import Beatmap, BeatmapDiff
import os
import random

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    map = Beatmap.query.order_by(func.random()).first()
    beatmap_card = []
    if map:
        maps_dir = os.path.join(current_app.instance_path, 'maps')
        map_name = os.path.splitext(os.path.basename(map.filepath))[0]
        folder = os.path.join(maps_dir, map_name)
        cover_img = None
        
        if os.path.isdir(folder):
            imgs = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            if imgs:
                cover_img = os.path.join('maps', map_name, random.choice(imgs))

        difficulties = BeatmapDiff.query.filter_by(map_id=map.id).all()
        difficulty_list = []
        for d in difficulties:
            difficulty_dict = {
                'name': d.map_name,
                'star': d.star_diff
            }
            difficulty_list.append(difficulty_dict)

        beatmap_card.append({
                'id': map.id,
                'name': map.name,
                'artist': map.artist,
                'uploader': map.uploader,
                'cover_img': cover_img,
                'difficulties': difficulty_list
            })
    return render_template('pages/home.html', beatmaps=beatmap_card)

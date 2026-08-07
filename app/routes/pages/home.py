from flask import Blueprint, render_template, current_app
from sqlalchemy.sql.expression import func
from app.models import Beatmap, BeatmapDiff, User
import os
import random

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    """
    Render the home page with a featured beatmap card.

    Inputs:
        - GET: None

    Processing:
        - Select a random beatmap.
        - Gather its cover image, difficulties, and uploader details.

    Outputs:
        - Renders the home page with the featured beatmap data.
    """
    # Pick a random featured beatmap so the home page feels varied.
    map = Beatmap.query.order_by(func.random()).first()
    beatmap_card = []
    # Gather all relevant data for the featured beatmap.
    if map:
        maps_dir = os.path.join(current_app.instance_path, 'maps')
        map_name = os.path.splitext(os.path.basename(map.filepath))[0]
        folder = os.path.join(maps_dir, map_name)
        cover_img = None

        if os.path.isdir(folder):
            imgs = [f for f in os.listdir(folder) if f.lower().endswith((
                '.jpg',
                '.jpeg',
                '.png',
                '.webp'))]
            if imgs:
                cover_img = os.path.join('maps', map_name, random.choice(imgs))

        # Collect the beatmap's available difficulties.
        difficulties = BeatmapDiff.query.filter_by(map_id=map.id).all()
        difficulty_list = []
        for d in difficulties:
            difficulty_dict = {
                'name': d.map_name,
                'star': d.star_diff
            }
            difficulty_list.append(difficulty_dict)

        user = User.query.get(map.uploader)
        # Hide the uploader name when the user has chosen to keep it private.
        if user:
            uploader = "********" if user.uploader_h else user.username
        else:
            uploader = "anonymous"

        beatmap_card.append({
                'id': map.id,
                'name': map.name,
                'artist': map.artist,
                'uploader': uploader,
                'cover_img': cover_img,
                'difficulties': difficulty_list
            })
    return render_template('pages/home.html', beatmaps=beatmap_card)

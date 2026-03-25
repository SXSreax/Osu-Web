from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request
from flask_login import current_user, login_required
from app.models import Beatmap, BeatmapDiff, Discussion, User
import os
import random

user_hub_bp = Blueprint('user_hub', __name__)

@user_hub_bp.route('/user_hub/')
@login_required
def user_hub():
    maps = Beatmap.query.filter_by(uploader=current_user.username)

    beatmap_card = []
    maps_dir = os.path.join(current_app.instance_path, 'maps')

    for bms in maps:
        map_name = os.path.splitext(os.path.basename(bms.filepath))[0]
        folder = os.path.join(maps_dir, map_name)
        cover_img = None

        if os.path.isdir(folder):
            imgs = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            if imgs:
                cover_img = os.path.join('maps', map_name, random.choice(imgs))

        difficulties = BeatmapDiff.query.filter_by(map_id=bms.id).all()
        difficulty_list = []
        for d in difficulties:
            difficulty_list.append({
                'name': d.map_name,
                'star': d.star_diff
            })

        beatmap_card.append({
            'id': bms.id,
            'name': bms.name,
            'artist': bms.artist,
            'uploader': bms.uploader,
            'cover_img': cover_img,
            'difficulties': difficulty_list
        })
    
    ds_card = Discussion.query.filter_by(user_id=current_user.id).all()

    discussions = []
    for ds in ds_card:
        user = User.query.get(ds.user_id)

    for ds in ds_card:
        discussions.append({
            'id': ds.id,
            'title': ds.title,
            'content': ds.content,
            'user': {
                'name': user.username if user else "Unknown",
                'avatar': user.avatar if user else None
            }
        })

    return render_template('pages/user_hub.html', beatmaps=beatmap_card, discussions=discussions)

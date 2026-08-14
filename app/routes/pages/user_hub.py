from flask import (Blueprint,
                   render_template,
                   flash,
                   redirect,
                   url_for,
                   current_app,
                   request)
from flask_login import current_user, login_required
from app.models import Beatmap, BeatmapDiff, Discussion, User, db
import os
import random

user_hub_bp = Blueprint('user_hub', __name__)


@user_hub_bp.route('/user_hub/')
@login_required
def user_hub():
    """
    Render the current user's hub with their beatmaps and discussions.

    Inputs:
        - GET: None

    Processing:
        - Load the user's uploaded beatmaps and discussions.
        - Prepare display data for both sections.

    Outputs:
        - Renders the user hub page with the prepared beatmap and discussion
            lists.
    """
    # Only load the current user's uploads for this hub page.
    maps = Beatmap.query.filter_by(uploader=current_user.id)

    beatmap_card = []
    maps_dir = os.path.join(current_app.instance_path, 'maps')

    # Gather beatmap card data for the current user's uploads.

    for bms in maps:
        map_name = os.path.splitext(os.path.basename(bms.filepath))[0]
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

        if bms.uploader_user:
            if bms.uploader_user.uploader_h:
                uploader = "********"
            else:
                uploader = bms.uploader_user.username
        else:
            uploader = "anonymous"

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
            'uploader': uploader,
            'cover_img': cover_img,
            'difficulties': difficulty_list
        })

    # Gather the current user's discussion entries for display.
    # Only show discussions created by the signed-in user.
    ds_card = Discussion.query.filter_by(user_id=current_user.id).all()

    discussions = []
    for ds in ds_card:
        user = User.query.get(ds.user_id)

    for ds in ds_card:
        discussions.append({
            'id': ds.id,
            'title': ds.title,
            'content': ds.content,
            'like': ds.like,
            'user': {
                'name': user.username if user else "Unknown",
                'avatar': user.avatar if user else None
            }
        })

    return render_template('pages/user_hub.html',
                           beatmaps=beatmap_card,
                           discussions=discussions)


@user_hub_bp.route("/user_hub/hide", methods=["POST"])
@login_required
def hide():
    """
    Update the current user's uploader visibility preference.

    Inputs:
        - POST: hide_uploader flag from the form

    Processing:
        - Save the visibility preference to the current user record.

    Outputs:
        - Redirects the user back to the user hub page.
    """
    # Persist the visibility preference so it applies across the site.
    current_user.uploader_h = request.form.get("hide_uploader") == "1"
    db.session.commit()
    flash("Uploader visibility updated", "success")
    return redirect(url_for("user_hub.user_hub"))

from flask import Blueprint, render_template, current_app, send_file, jsonify
from flask_login import current_user
import os
import random
import zipfile
import io
from app.models import db, Beatmap, BeatmapDiff, Favorite, User

map_bp = Blueprint('map', __name__)


@map_bp.route('/map/<int:beatmap_id>')
def map_detail(beatmap_id):
    """
    Render the beatmap detail page.

    Inputs:
        - GET: beatmap ID from the route

    Processing:
        - Load the beatmap and related metadata.
        - Gather cover art, difficulty data, and favorite state.

    Outputs:
        - Renders the beatmap detail page with the prepared data.
    """
    bm = Beatmap.query.get_or_404(beatmap_id)

    maps_dir = os.path.join(current_app.instance_path, 'maps')
    base_name = os.path.splitext(os.path.basename(bm.filepath))[0]
    folder = os.path.join(maps_dir, base_name)

    # Find a cover image from the beatmap folder when available.
    cover_img = None
    if os.path.isdir(folder):
        # Use a random image from the beatmap folder when a cover is available.
        imgs = [f for f in os.listdir(folder) if f.lower().endswith((
            '.jpg',
            '.jpeg',
            '.png',
            '.webp'
            ))]
        if imgs:
            cover_img = os.path.join('maps', base_name, random.choice(imgs))

    if bm.uploader_user:
        if bm.uploader_user.uploader_h:
            uploader = "********"
        else:
            uploader = bm.uploader_user.username
    else:
        uploader = "anonymous"

    # Gather all difficulty entries for this beatmap.
    difficulties = BeatmapDiff.query.filter_by(map_id=bm.id).all()
    difficulty_list = []
    for d in difficulties:
        difficulty_dict = {
            'name': d.map_name,
            'star': d.star_diff,
            'hp': d.hp,
            'od': d.od,
            'cs': d.cs,
            'ar': d.ar,
            'kc': d.kc
        }
        difficulty_list.append(difficulty_dict)

    # Check whether the current user has already favorited this beatmap.
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
        'mode': bm.mode,
        'difficulties': difficulty_list,
    }, favorited=favorited)


@map_bp.route('/map/download/<int:beatmap_id>/<format>')
def download_beatmap(beatmap_id, format):
    """
    Download a beatmap folder as a zip or osz archive.

    Inputs:
        - GET: beatmap ID and download format from the route

    Processing:
        - Locate the beatmap folder.
        - Package its files into a zip archive.

    Outputs:
        - Returns the archive as a downloadable file.
    """
    bm = Beatmap.query.get_or_404(beatmap_id)

    maps_dir = os.path.join(current_app.instance_path, 'maps')
    base_name = os.path.splitext(os.path.basename(bm.filepath))[0]
    folder = os.path.join(maps_dir, base_name)

    if not os.path.isdir(folder):
        return 'Beatmap folder not found', 404

    # Build the archive from all files in the beatmap folder.
    # Create a temporary archive in memory so the download can be
    # streamed without writing to disk.
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, folder))

    zip_buffer.seek(0)
    extension = 'osz' if format.lower() == 'osz' else 'zip'
    return send_file(zip_buffer,
                     mimetype='application/zip',
                     as_attachment=True,
                     download_name=f"{base_name}.{extension}")


@map_bp.route('/map/<int:beatmap_id>/favorite', methods=['POST'])
def favorite(beatmap_id):
    """
    Toggle the favorite status for a beatmap.

    Inputs:
        - POST: beatmap ID from the route

    Processing:
        - Check whether the beatmap is already favorited.
        - Add or remove the favorite record.

    Outputs:
        - Returns JSON indicating whether the favorite was added or removed.
    """
    existing = Favorite.query.filter_by(
        user_id=current_user.id,
        map_id=beatmap_id).first()

    if existing:
        db.session.delete(existing)
        status = "removed"
    else:
        db.session.add(Favorite(user_id=current_user.id, map_id=beatmap_id))
        status = "added"

    db.session.commit()
    return jsonify({"status": status})

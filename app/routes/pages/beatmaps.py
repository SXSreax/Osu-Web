from flask import Blueprint, render_template, jsonify, current_app
from app.models import Beatmap, BeatmapDiff, User
from app.forms import SearchForm
from app.utils.files import serve_instance_file
import os
import random
from urllib.parse import quote

beatmaps_bp = Blueprint('beatmaps', __name__)


@beatmaps_bp.route('/beatmaps/')
def beatmaps():
    """
    Render the beatmaps listing page.

    Inputs:
        - GET: None

    Processing:
        - Fetch all beatmaps from the database.
        - Build card data with cover images, uploader details,
            and difficulty information.
        - Pass the prepared data to the beatmaps template.

    Outputs:
        - Renders the beatmaps page with the collected card data.
    """
    form = SearchForm()
    maps = Beatmap.query.all()
    beatmap_card = []
    # Gather all relevant data for each beatmap.
    for bms in maps:
        maps_dir = os.path.join(current_app.instance_path, 'maps')
        map_name = os.path.splitext(os.path.basename(bms.filepath))[0]
        folder = os.path.join(maps_dir, map_name)
        cover_img = None

        if os.path.isdir(folder):
            imgs = [f for f in os.listdir(folder) if f.lower().endswith((
                '.jpg',
                '.jpeg',
                '.png',
                '.webp'
                ))]
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
    return render_template('pages/beatmaps.html',
                           beatmaps=beatmap_card,
                           form=form)


@beatmaps_bp.route('/instance/<path:filepath>')
def instance(filepath):
    """
    Serve a file from the instance directory.

    Inputs:
        - GET: a relative file path

    Processing:
        - Forward the requested path to the instance file-serving helper.

    Outputs:
        - Returns the requested file from the instance directory.
    """
    return serve_instance_file(filepath)


@beatmaps_bp.route('/get-beatmap-audio/<int:beatmap_id>')
def get_beatmap_audio(beatmap_id):
    """
    Return an audio file URL for a beatmap.

    Inputs:
        - GET: beatmap ID from the route parameter

    Processing:
        - Fetch the beatmap record.
        - Search the beatmap folder for supported audio files.
        - Select the first valid candidate and build a URL.

    Outputs:
        - Returns the audio URL as JSON.
        - Returns an error message if no suitable audio file is found.
    """
    bms = Beatmap.query.get(beatmap_id)
    if not bms:
        return jsonify({'error': 'Beatmap not found'}), 404

    maps_dir = os.path.join(current_app.instance_path, 'maps')
    base_name = os.path.splitext(os.path.basename(bms.filepath))[0]
    folder = os.path.join(maps_dir, base_name)

    if not os.path.isdir(folder):
        return jsonify({'error': 'No audio folder found'}), 404

    audio_extensions = ('.mp3',
                        '.ogg',
                        '.m4a',
                        '.flac',
                        '.wav',
                        '.aac',
                        '.wma')

    # Scan the beatmap folder for supported audio files.
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


@beatmaps_bp.route('/search/', methods=["POST"])
def search():
    """
    Search for beatmaps based on form input.

    Inputs:
        - POST: search text from the form

    Processing:
        - Validate the submitted search form.
        - Query beatmaps by ID, name, artist, or uploader.
        - Build result cards with cover images and difficulty data.

    Outputs:
        - Renders the search results page with the collected beatmap data.
    """
    form = SearchForm()
    beatmap_card = []
    q = ""
    results = []

    if form.validate_on_submit():
        q = form.search.data
        maps_dir = os.path.join(current_app.instance_path, 'maps')

        if q:
            # Search by several fields so users can find maps by ID,
            # name, artist, or uploader.
            search = f"%{q}%"
            results = Beatmap.query.filter(
                Beatmap.id.ilike(search)
                | Beatmap.name.ilike(search)
                | Beatmap.artist.ilike(search)
                | User.username.ilike(search)
            ).limit(100).all()

        # Gather all relevant data for each search result.
        for bms in results:
            map_name = os.path.splitext(os.path.basename(bms.filepath))[0]
            folder = os.path.join(maps_dir, map_name)
            cover_img = None

            if os.path.isdir(folder):
                imgs = [f for f in os.listdir(folder) if f.lower().endswith((
                    '.jpg',
                    '.jpeg',
                    '.png',
                    '.webp'
                    ))]
                if imgs:
                    cover_img = os.path.join('maps',
                                             map_name,
                                             random.choice(imgs))

            difficulties = BeatmapDiff.query.filter_by(map_id=bms.id).all()
            difficulty_list = []
            for d in difficulties:
                difficulty_list.append({
                    'name': d.map_name,
                    'star': d.star_diff
                })

            if bms.uploader_user:
                if bms.uploader_user.uploader_h:
                    uploader = "********"
                else:
                    uploader = bms.uploader_user.username
            else:
                uploader = "anonymous"

            beatmap_card.append({
                'id': bms.id,
                'name': bms.name,
                'artist': bms.artist,
                'uploader': uploader,
                'cover_img': cover_img,
                'difficulties': difficulty_list
            })

    return render_template(
        "pages/search.html",
        form=form,
        beatmaps=beatmap_card,
        searches=q
    )

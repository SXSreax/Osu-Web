from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   flash,
                   current_app)
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
import os
import re
import zipfile
import requests
import shutil
import tempfile

from app.models import db, Beatmap, BeatmapDiff
from app.forms import UploadForm

upload_bp = Blueprint('upload', __name__)


def fetch_star_rate(beatmapset_id: int, beatmap_id: int, mode: int):
    """
    Fetch difficulty rating data for a specific beatmap and mode.

    Inputs:
        - beatmapset ID, beatmap ID, and mode number

    Processing:
        - Request an OAuth token from the osu! API.
        - Query the API for the beatmap's difficulty rating.

    Outputs:
        - Returns the beatmap's difficulty rating as a number.
    """
    # Request an access token from the osu! API.
    token_res = requests.post(
        "https://osu.ppy.sh/oauth/token",
        json={
            "client_id": current_app.config["OSU_CLIENT_ID"],
            "client_secret": current_app.config["OSU_CLIENT_SECRET"],
            "grant_type": "client_credentials",
            "scope": "public"
        }
    )
    token_res.raise_for_status()
    token = token_res.json().get("access_token")

    headers = {"Authorization": f"Bearer {token}"}
    mode_map = {
        0: 'osu',
        1: 'taiko',
        2: 'fruits',
        3: 'mania'
    }
    # Fall back to osu! when an unknown mode is returned by the source file.
    mode_name = mode_map.get(mode, 'osu')
    url = f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}?mode={mode_name}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    return data.get("difficulty_rating")


def get_file_info(beatmap_path):
    """
    Extract beatmap metadata from an .osu file.

    Inputs:
        - Path to an .osu file

    Processing:
        - Read the file content and parse metadata and difficulty sections.
        - Extract values such as title, artist, IDs, and gameplay stats.

    Outputs:
        - Returns a tuple containing the parsed beatmap information.
    """
    map_name = os.path.basename(beatmap_path)
    beatmap_id = None
    beatmapset_id = None
    mode = None
    artist = None
    title = None
    hp = None
    od = None
    cs = None
    ar = None
    kc = None

    try:
        # Read the .osu file using UTF-8 first, then fall back to Latin-1.
        try:
            with open(beatmap_path, 'r', encoding='utf-8') as f:
                content = f.read()
        # Some legacy beatmap files are not UTF-8, so retry with Latin-1.
        except UnicodeDecodeError:
            with open(beatmap_path, 'r', encoding='latin-1') as f:
                content = f.read()

        current_section = None
        lines = content.splitlines()
        version = None

        # Parse the .osu file section by section.
        for line in lines:
            line = line.strip()
            # Ignore blank lines and comments because they carry no metadata.
            if not line or line.startswith('//'):
                continue

            # Track the active section so identical keys mean the right thing.
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].lower()
                continue

            # Read the gameplay mode from the General section only.
            if current_section == 'general':
                if line.startswith('Mode:'):
                    m = re.match(r'Mode\s*:\s*(\d+)', line)
                    # Store the mode only when the value is a valid integer.
                    if m:
                        mode = int(m.group(1))

            # Parse numeric gameplay settings from the Difficulty section.
            if current_section == 'difficulty':
                m = re.match(
                    r'(?:HPDrainRate|HPDrain)\s*:\s*([0-9.+-eE]+)',
                    line
                    )
                if m:
                    try:
                        hp = float(m.group(1))
                    # Invalid numeric metadata should not reject the file.
                    except ValueError:
                        hp = None

                m = re.match(r'OverallDifficulty\s*:\s*([0-9.+-eE]+)', line)
                if m:
                    try:
                        od = float(m.group(1))
                    except ValueError:
                        od = None

                m = re.match(r'CircleSize\s*:\s*([0-9.+-eE]+)', line)
                if m:
                    try:
                        cs = float(m.group(1))
                    except ValueError:
                        cs = None

                m = re.match(r'ApproachRate\s*:\s*([0-9.+-eE]+)', line)
                if m:
                    try:
                        ar = float(m.group(1))
                    except ValueError:
                        ar = None

            if current_section == 'metadata':
                if line.startswith('Title:') and title is None:
                    m = re.match(r'Title\s*:\s*(.+)', line)
                    if m:
                        title = m.group(1).strip()

                elif line.startswith('Artist:') and artist is None:
                    m = re.match(r'Artist\s*:\s*(.+)', line)
                    if m:
                        artist = m.group(1).strip()

                elif line.startswith('Version:') and version is None:
                    m = re.match(r'Version\s*:\s*(.+)', line)
                    if m:
                        version = m.group(1).strip()

                elif line.startswith('BeatmapID:'):
                    m = re.match(r'BeatmapID\s*:\s*(\d+)', line)
                    if m:
                        beatmap_id = int(m.group(1))

                elif line.startswith('BeatmapSetID:'):
                    m = re.match(r'BeatmapSetID\s*:\s*(\d+)', line)
                    if m:
                        beatmapset_id = int(m.group(1))

        # Prefer a title plus version for the display name when available.
        if title:
            if version:
                map_name = f"{title} [{version}]"
            else:
                map_name = title

    except Exception as e:
        print(f"Error extracting IDs from {beatmap_path}: {e}")

    # Mania maps use key count instead of circle size.
    # Mania stores key count in CircleSize, so convert it separately.
    if mode == 3 and cs is not None:
        try:
            kc = int(cs)
        except Exception:
            kc = None

    return (map_name,
            beatmap_id,
            beatmapset_id,
            mode,
            artist,
            title,
            hp,
            od,
            cs,
            ar,
            kc)


def sanitize_id(filename):
    name, ext = os.path.splitext(filename)
    match = re.match(r'^(\d+)', name)
    name = match.group(1)
    return name + ext.lower()


def sanitize_filename(filename):
    name, ext = os.path.splitext(filename)
    name = re.sub(r'[^\w\s\-\(\)]', '_', name)
    return name + ext


@upload_bp.route('/upload/')
@login_required
def upload():
    """
    Render the upload page.

    Inputs:
        - GET: None

    Processing:
        - Create an upload form for the user.

    Outputs:
        - Renders the upload page.
    """
    form = UploadForm()
    return render_template('pages/upload.html', form=form)


@upload_bp.route('/upload/store', methods=['POST'])
def upload_store():
    """
    Store an uploaded beatmap archive and process its contents.

    Inputs:
        - POST: uploaded .osz or .zip file from the form

    Processing:
        - Validate the uploaded archive.
        - Extract the files and locate the .osu data.
        - Save the beatmap package and store difficulty metadata.

    Outputs:
        - Redirects back to the home page with a success or error message.
    """
    form = UploadForm()
    # Reject invalid form data before saving or inspecting the upload.
    if not form.validate_on_submit():
        flash('Please upload a valid file', "error")
        return render_template('pages/upload.html', form=form)

    # Collect the uploaded archive and current user information.
    # Store the current user's ID as the uploader for the uploaded beatmap.
    uploaded_file = form.file.data
    uploader = current_user.id

    # Accept only uploads with the archive extensions handled below.
    if not uploaded_file or not (
         uploaded_file.filename.endswith('.osz') or
         uploaded_file.filename.endswith('.zip')):
        flash('Only accept .osz or .zip files.', "error")
        return redirect(url_for('upload.upload'))

    filename = secure_filename(uploaded_file.filename)

    with tempfile.TemporaryDirectory(dir=os.path.join(
         current_app.instance_path, 'temp_uploads')) as temp_dir:
        # Use a temporary directory so extracted files do not pollute
        # the app permanently.
        temp_zip_path = os.path.join(temp_dir, filename)
        uploaded_file.save(temp_zip_path)

        # Extract the archive into a temporary folder for inspection.
        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_dir, exist_ok=True)

        # Extraction is isolated so a malformed archive can be reported safely.
        try:
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except zipfile.BadZipFile:
            flash('The uploaded file is not a valid zip archive.', "error")
            return redirect(url_for('upload.upload'))

        # Find the first .osu file inside the extracted archive.
        osu_file_path = None
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                # The first .osu file supplies the set-level metadata.
                if file.endswith('.osu'):
                    osu_file_path = os.path.join(root, file)
                    break
            if osu_file_path:
                break

        # Stop when the archive contains assets but no beatmap definition.
        if not osu_file_path:
            flash('The archive does not contain any .osu file.', "error")
            return redirect(url_for('upload.upload'))

        (_, _, beatmapset_id, mode_from_file, artist, title, hp0, od0,
         cs0, ar0, kc0) = get_file_info(osu_file_path)

        # These fields are required to create a usable beatmap record.
        if not beatmapset_id or not artist or not title:
            flash('Could not extract necessary metadata (BeatmapSetID, '
                  'Artist, Title) from the .osu file.', "error")
            return redirect(url_for('upload.upload'))

        # Prepare the permanent storage location for the beatmap files.
        maps_dir = os.path.join(current_app.instance_path, 'maps')
        os.makedirs(maps_dir, exist_ok=True)

        final_extract_folder = os.path.join(maps_dir, str(beatmapset_id))
        final_zip_path = os.path.join(maps_dir, str(beatmapset_id) + '.zip')

        # Replace old files so re-uploading a set removes stale assets.
        if os.path.exists(final_extract_folder):
            shutil.rmtree(final_extract_folder)

        # Handle archives that contain a single top-level folder.
        extracted_items = os.listdir(extract_dir)
        source_dir = extract_dir
        # Unwrap archives that place all files inside one top-level directory.
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(
             extract_dir, extracted_items[0])):
            source_dir = os.path.join(extract_dir, extracted_items[0])

        shutil.copytree(source_dir, final_extract_folder)

        shutil.copy(temp_zip_path, final_zip_path)

        relative_path = os.path.join('maps', str(beatmapset_id) + '.zip')

        # Update an existing beatmap record instead of creating
        # duplicates when the same set is uploaded again.
        # Upsert the set record so repeated uploads do not create duplicates.
        existing = Beatmap.query.get(beatmapset_id)
        # Update the existing row while preserving its database identity.
        if existing:
            existing.name = title
            existing.artist = artist
            existing.uploader = uploader
            existing.filepath = relative_path
            # Keep a previously known mode when the new file omits it.
            if mode_from_file is not None:
                existing.mode = mode_from_file
        else:
            # Insert a new set with a neutral osu! mode when none was parsed.
            beatmap = Beatmap(
                id=beatmapset_id,
                name=title,
                artist=artist,
                uploader=uploader,
                filepath=relative_path,
                mode=mode_from_file if mode_from_file is not None else 0
            )
            db.session.add(beatmap)
        # Persist set metadata before creating its individual difficulties.
        db.session.commit()

        try:
            # Process every .osu file found in the extracted beatmap folder.
            osu_files = [
                 f for f in os.listdir(final_extract_folder)
                 if f.endswith('.osu')]
            modes_found = set()
            # Parse and upsert every difficulty definition in the set.
            for osu_file in osu_files:
                osu_path = os.path.join(final_extract_folder, osu_file)
                (map_name_file,
                 beatmap_id_file,
                 beatmapset_id_file,
                 mode_file,
                 artist_file,
                 title_file,
                 hp_file,
                 od_file,
                 cs_file,
                 ar_file,
                 kc_file) = get_file_info(osu_path)

                # Skip files that do not expose a parseable mode to
                # avoid bad difficulty rows.
                # Without a mode, the row cannot be mapped to gameplay fields.
                if mode_file is None:
                    continue

                modes_found.add(mode_file)

                # Skip files without IDs needed for API and database lookups.
                if not (beatmap_id_file and beatmapset_id_file):
                    continue

                # Star ratings come from osu!'s API and may fail independently.
                try:
                    star_rating = fetch_star_rate(beatmapset_id_file,
                                                  beatmap_id_file,
                                                  mode_file)
                except Exception as e:
                    print(f"Failed to fetch star for {osu_file}: {e}")
                    continue

                # Do not store a difficulty when the API returned no rating.
                if star_rating is None:
                    continue

                star_truncated = int(star_rating * 100) / 100

                # Match a row by set and difficulty name for an upsert.
                existing_diff = BeatmapDiff.query.filter_by(
                    map_id=beatmapset_id_file,
                    map_name=map_name_file
                ).first()

                relative_diff_path = os.path.join(
                    'maps', str(beatmapset_id_file),
                    osu_file)

                # assign fields according to mode
                # Update the existing difficulty so metadata stays current.
                if existing_diff:
                    existing_diff.star_diff = star_truncated
                    existing_diff.filepath = relative_diff_path
                    # Each mode exposes a different subset of gameplay fields.
                    if mode_file == 0:  # osu
                        existing_diff.cs = cs_file
                        existing_diff.hp = hp_file
                        existing_diff.od = od_file
                        existing_diff.ar = ar_file
                    elif mode_file == 1:  # taiko
                        existing_diff.hp = hp_file
                        existing_diff.od = od_file
                    elif mode_file == 2:  # catch
                        existing_diff.cs = cs_file
                        existing_diff.hp = hp_file
                        existing_diff.od = od_file
                        existing_diff.ar = ar_file
                    elif mode_file == 3:  # mania
                        existing_diff.kc = kc_file
                        existing_diff.hp = hp_file
                        existing_diff.od = od_file
                else:
                    # Build a new difficulty row when this map/version is new.
                    diff_kwargs = dict(
                        map_id=beatmapset_id_file,
                        map_name=map_name_file,
                        star_diff=star_truncated,
                        filepath=relative_diff_path
                    )
                    # add mode-specific fields
                    # Populate only the fields supported by the parsed mode.
                    if mode_file == 0:  # osu
                        diff_kwargs.update(dict(cs=cs_file,
                                                hp=hp_file,
                                                od=od_file,
                                                ar=ar_file))
                    elif mode_file == 1:  # taiko
                        diff_kwargs.update(dict(hp=hp_file,
                                                od=od_file))
                    elif mode_file == 2:  # catch
                        diff_kwargs.update(dict(cs=cs_file,
                                                hp=hp_file,
                                                od=od_file,
                                                ar=ar_file))
                    elif mode_file == 3:  # mania
                        diff_kwargs.update(dict(kc=kc_file,
                                                hp=hp_file,
                                                od=od_file))

                    beatmap_diff = BeatmapDiff(**diff_kwargs)
                    # Stage the new difficulty for the batch commit below.
                    db.session.add(beatmap_diff)

            # Commit all difficulty updates together after processing the set.
            db.session.commit()

        # Keep the set upload successful even when rating enrichment fails.
        except Exception as e:
            print(f"Error fetching/storing star ratings: {e}")
            flash("Beatmap uploaded but failed to fetch star ratings.",
                  "warning")
            return redirect(url_for('upload.upload'))

        # Report the modes successfully discovered for user feedback.
        if modes_found:
            mode_names = {0: 'osu', 1: 'taiko', 2: 'catch', 3: 'mania'}
            readable = ", ".join(
                sorted({mode_names.get(m, str(m)) for m in modes_found}))
            flash(
                f'Beatmap updated successfully (modes processed: {readable}).',
                'success')
        else:
            flash("No beatmap modes were processed.", "warning")

    return redirect(url_for('home.home'))

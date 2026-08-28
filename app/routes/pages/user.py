from flask import (Blueprint,
                   render_template,
                   flash,
                   redirect,
                   url_for,
                   current_app,
                   request,
                   jsonify,
                   session)
from flask_login import current_user, login_required
from flask_mail import Message
from app.extensions import mail
from app.models import db, BeatmapDiff, User
from app.forms import UserEditForm, VerifyForm
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os
import pyotp
import time
import random

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/')
@login_required
def user():
    """
    Render the current user's profile page.

    Inputs:
        - GET: None

    Processing:
        - Load the user's favorite beatmaps and discussions.
        - Prepare display data for the profile template.

    Outputs:
        - Renders the user profile page with the collected favorites and
            verification form.
    """
    # Load the current user's favorite beatmaps from the relationship table.
    # Load beatmaps through the current user's favorite relationship.
    favorite_maps = [fav.beatmap for fav in current_user.favorites]

    beatmap_card = []
    maps_dir = os.path.join(current_app.instance_path, 'maps')

    # Gather favorite beatmap cards for the profile page.

    # Build display cards for each favorited beatmap.
    for bms in favorite_maps:
        map_name = os.path.splitext(os.path.basename(bms.filepath))[0]
        folder = os.path.join(maps_dir, map_name)
        cover_img = None

        # Artwork is optional, so render the card even without a folder.
        if os.path.isdir(folder):
            imgs = [
                f for f in os.listdir(folder)
                if f.lower().endswith((
                    '.jpg',
                    '.jpeg',
                    '.png',
                    '.webp',
                    'gif'
                ))
            ]

            common_backgrounds = [
                'bg.jpg',
                'background.jpg',
                'background.png',
                'bg.png',
                'BG.jpg',
                'background@2x.jpg',
                'bg_1.jpg',
                'bg2.jpg'
            ]

            matching_backgrounds = [
                f for f in common_backgrounds
                if f in imgs
            ]

            # Prefer the standard background filename when it exists.
            if matching_backgrounds:
                # Use the first matching common background
                cover_img = os.path.join(
                    'maps',
                    map_name,
                    matching_backgrounds[0]
                )

            # Fall back to another supported image when needed.
            elif imgs:
                # No common background found, choose a random image
                cover_img = os.path.join(
                    'maps',
                    map_name,
                    random.choice(imgs)
                )

        # Query the difficulty metadata for this favorited beatmap.
        difficulties = BeatmapDiff.query.filter_by(map_id=bms.id).all()
        difficulty_list = []
        for d in difficulties:
            difficulty_list.append({
                'name': d.map_name,
                'star': d.star_diff
            })

        # Respect the uploader's privacy preference in the favorite card.
        if bms.uploader_user:
            # Mask the uploader name when hidden mode is enabled.
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

    # Gather the user's favorite discussions for display.
    # Load favorite discussions so the profile page can show them.
    # Load discussions through the current user's favorite relationship.
    favorite_discussion = [
        fav.discussion for fav in current_user.favorited_discussions]

    discussions = []
    # Resolve each discussion author for the profile card.
    for ds in favorite_discussion:
        user = User.query.get(ds.user_id)

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

    form = VerifyForm()
    return render_template("pages/user.html",
                           beatmaps=beatmap_card,
                           discussions=discussions,
                           form=form)


@user_bp.route('/user/verify/', methods=["POST"])
@login_required
def verify():
    """
    Verify the user's identity before allowing profile settings access.

    Inputs:
        - POST: JSON action data or a verification form submission

    Processing:
        - Send a one-time verification code when needed.
        - Validate the submitted code and update the session state.

    Outputs:
        - Returns JSON for verification flow steps or redirects to the profile
            edit page.
    """
    current_app.logger.info(
        f"User {current_user.id} triggered settings-action")

    key = current_app.config["TOTP_KEY"]
    totp = pyotp.TOTP(key, interval=60)
    print(totp.now())

    # JSON requests drive the modal's pre-verification and email flow.
    if request.is_json:
        # Handle the JSON-based verification flow for the settings modal.
        data = request.get_json(silent=True) or {}
        # Only the settings action needs to inspect verification state.
        if data.get("action") == "open_settings":
            expiry = session.get("settings_verified_until", 0)
            attempts = session.get("settings_attempts", 0)

            # Reuse an unexpired verification session while attempts remain.
            if expiry and expiry > time.time() and attempts > 0:
                return jsonify(success=True,
                               verified=True,
                               redirect=url_for("user.user_edit"))

            reason = None
            # Record why a previous verification session cannot be reused.
            if attempts <= 0:
                reason = "attempts_exhausted"
            elif expiry and expiry <= time.time():
                reason = "expired"

            session.pop("settings_verified_until", None)
            session.pop("settings_attempts", None)

            # Send the verification code by email so the user can
            # confirm their identity.
            msg = Message(
                "Verification Code from Osu!Web",
                sender="osuweb123@gmail.com",
                recipients=[current_user.email],
            )
            msg.body = (
                f"Thank you for keeping up with us.\n"
                f"You will have 1 minute to enter the "
                f"code before it expires.\n"
                f"Verification code: {totp.now()}"
            )
            # Email delivery can fail independently of the session workflow.
            try:
                mail.send(msg)
                return jsonify(
                    success=True,
                    message="Please verify again.",
                    requires_verification=True,
                    reason=reason,
                )
            except Exception as e:
                current_app.logger.error(
                    f"Email send failed for user {current_user.id}: {e}")
                return jsonify(success=False, message=str(e)), 500

    form = VerifyForm()
    # Validate the submitted code before changing session permissions.
    if form.validate_on_submit():
        # Validate the submitted one-time password from the form.
        code = str(form.code.data).zfill(6)

        # A valid one-time code grants temporary access to profile settings.
        if totp.verify(code, valid_window=1):
            timeout = 30 * 60
            attempts = 11
            session["settings_verified_until"] = int(time.time()) + timeout
            session["settings_attempts"] = attempts
            flash("Verification successful.", "success")
            return redirect(url_for("user.user_edit"))
        else:
            flash("Invalid verification code. Please try again.", "error")
    else:
        # Surface form validation errors before returning to the profile page.
        for error in form.code.errors:
            flash(error, "error")

    return redirect(url_for("user.user"))


@user_bp.route('/user/edit/', methods=["GET", "POST"])
@login_required
def user_edit():
    """
    Allow the current user to edit profile information and upload images.

    Inputs:
        - GET: None
        - POST: profile form data and optional image uploads

    Processing:
        - Check verification status before allowing edits.
        - Update profile fields and save uploaded avatar or banner files.

    Outputs:
        - Renders the edit page or redirects back to the profile after saving.
    """
    expiry = session.get("settings_verified_until", 0)
    attempts = session.get("settings_attempts", 0)
    # Expired verification must be cleared before redirecting to the profile.
    if expiry < time.time():
        session.pop("settings_verified_until", None)
        flash("Please verify your identity first. Use the setting button",
              "error")
        return redirect(url_for("user.user"))

    # Block edits after the allowed number of settings requests is exhausted.
    if attempts <= 0:
        flash("Too many attempts, please verify again later.", "error")
        return redirect(url_for("user.user"))

    session["settings_attempts"] -= 1
    form = UserEditForm()

    # GET requests populate the form; POST requests are handled below.
    if request.method == "GET":
        # Pre-fill the form with the current user's existing values.
        form.username.data = current_user.username
        form.email.data = current_user.email

    # Apply changes only after the profile form passes validation.
    if form.validate_on_submit():
        # Apply the profile changes submitted in the edit form.
        # Reset actions take priority over normal profile updates.
        if form.reset_avatar.data:
            # Reset the avatar to remove the current image from the profile.
            # Delete the stored file when a previous avatar is recorded.
            if current_user.avatar:
                # Remove the old image before saving a replacement to
                # avoid stale files.
                old_avatar = os.path.join(current_app.instance_path,
                                          'uploads',
                                          'avatar',
                                          current_user.avatar)
                os.remove(old_avatar)
            current_user.avatar = None
            # Commit the reset before redirecting back to the edit page.
            db.session.commit()
            flash("Avatar has been reset.", "success")
            session["settings_attempts"] += 1
            return redirect(url_for("user.user_edit"))

        # Handle banner reset using the same database and file cleanup rules.
        if form.reset_banner.data:
            # Reset the banner to remove the current header image.
            # Remove the old banner file when one is associated with the user.
            if current_user.banner:
                old_banner = os.path.join(current_app.instance_path,
                                          'uploads',
                                          'banner',
                                          current_user.banner)
                os.remove(old_banner)
            current_user.banner = None
            # Commit the banner reset before returning to the form.
            db.session.commit()
            flash("Banner has been reset.", "success")
            session["settings_attempts"] += 1
            return redirect(url_for("user.user_edit"))

        # Update optional profile fields only when a new value was submitted.
        if form.username.data:
            # Update the username when the user submits a new one.
            current_user.username = form.username.data

        if form.email.data:
            # Normalize the email before storing it to keep it consistent.
            current_user.email = form.email.data.lower()

        if form.new_password.data:
            # Hash the new password before saving it to the user record.
            current_user.set_password(form.new_password.data)

        # Replace the avatar only when the upload contains a file.
        if isinstance(form.avatar.data, FileStorage):
            # Save a new avatar file when the form includes an uploaded image.
            new_avatar = form.avatar.data
            new_avatar.stream.seek(0)
            filename = secure_filename(new_avatar.filename)
            ext = os.path.splitext(filename)[1]
            avatar_name = str(current_user.id) + ext
            avatar_path = os.path.join(current_app.instance_path,
                                       'uploads',
                                       'avatar',
                                       avatar_name)
            # Remove the previous file so extensions cannot leave stale assets.
            if current_user.avatar:
                old_avatar_path = os.path.join(current_app.instance_path,
                                               'uploads',
                                               'avatar',
                                               current_user.avatar)
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            new_avatar.save(avatar_path)
            current_user.avatar = avatar_name

        # Replace the banner only when the upload contains a file.
        if isinstance(form.banner.data, FileStorage):
            # Save a new banner file when the form includes an uploaded image.
            new_banner = form.banner.data
            new_banner.stream.seek(0)
            filename = secure_filename(new_banner.filename)
            ext = os.path.splitext(filename)[1]
            banner_name = str(current_user.id) + ext
            banner_path = os.path.join(current_app.instance_path,
                                       'uploads',
                                       'banner',
                                       banner_name)
            # Remove the previous banner before saving the replacement.
            if current_user.banner:
                old_banner_path = os.path.join(current_app.instance_path,
                                               'uploads',
                                               'banner',
                                               current_user.banner)
                if os.path.exists(old_banner_path):
                    os.remove(old_banner_path)
            new_banner.save(banner_path)
            current_user.banner = banner_name

        # Commit the profile changes once all updates are prepared.
        # Persist all profile field and file-name changes in one transaction.
        db.session.commit()

        flash("Profile updated successfully.", "success")
        session["settings_attempts"] += 1
        return redirect(url_for("user.user_edit"))

    return render_template("pages/user_edit.html", form=form)

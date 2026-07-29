from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request, jsonify, session
from flask_login import current_user, login_required
from flask_mail import Message
from app.extensions import mail
from app.models import db, BeatmapDiff, User
from app.forms import UserEditForm, VerifyForm
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os
import pyotp
import random

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/')
@login_required
def user():
    favorite_maps = [fav.beatmap for fav in current_user.favorites]

    beatmap_card = []
    maps_dir = os.path.join(current_app.instance_path, 'maps')

    for bms in favorite_maps:
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

        user = User.query.get(bms.uploader)
        if user:
            uploader = user.username
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

    favorite_discussion = [fav.discussion for fav in current_user.favorited_discussions]

    discussions = []
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
    return render_template("pages/user.html", beatmaps=beatmap_card, discussions=discussions, form=form)

@user_bp.route('/user/verify/', methods=["POST"])
@login_required
def verify():
    current_app.logger.info(f"User {current_user.id} triggered settings-action")

    key = current_app.config["TOTP_KEY"]
    totp = pyotp.TOTP(key, interval=60)

    if request.is_json:
        data = request.get_json(silent=True) or {}
        if data.get("action") == "open_settings":
            msg = Message(
                "Verification Code from Osu!Web",
                sender="osuweb123@gmail.com",
                recipients=[current_user.email],
            )
            msg.body = (
                    f"Thank you for keeping up with us.\n"
                    f"You will have 1 minute to enter the code before it expires.\n"
                    f"Verification code: {totp.now()}"
                )
            try:
                mail.send(msg)
                return jsonify(success=True, message="Email sent successfully")
            except Exception as e:
                current_app.logger.error(f"Email send failed for user {current_user.id}: {e}")
                return jsonify(success=False, message=str(e)), 500

    form = VerifyForm()
    if form.validate_on_submit():
        code = str(form.code.data).zfill(6)

        if totp.verify(code, valid_window=1):
            session["settings_verified"] = True
            flash("Verification successful.", "success")
            return redirect(url_for("user.user_edit"))
        else:
            flash("Invalid verification code. Please try again.", "error")
    else:
        for error in form.code.errors:
            flash(error, "error")

    return redirect(url_for("user.user"))


@user_bp.route('/user/edit/', methods=["GET", "POST"])
@login_required
def user_edit():
    if not session.get("settings_verified"):
        flash("Please verify your identity first. Use the setting button", "error")
        return redirect(url_for("user.user"))

    form = UserEditForm()

    if request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    if form.validate_on_submit():
        if form.reset_avatar.data:
            if current_user.avatar:
                old_avatar = os.path.join(current_app.instance_path, 'uploads', 'avatar', current_user.avatar)
                os.remove(old_avatar)
            current_user.avatar = None
            db.session.commit()
            flash("Avatar has been reset.", "success")
            return redirect(url_for("user.user_edit"))

        if form.reset_banner.data:
            if current_user.banner:
                old_banner = os.path.join(current_app.instance_path, 'uploads', 'banner', current_user.banner)
                os.remove(old_banner)
            current_user.banner = None
            db.session.commit()
            flash("Banner has been reset.", "success")
            return redirect(url_for("user.user_edit"))

        if form.username.data:
            current_user.username = form.username.data

        if form.email.data:
            current_user.email = form.email.data.lower()

        if form.new_password.data:
            current_user.set_password(form.new_password.data)

        if isinstance(form.avatar.data, FileStorage):
            new_avatar = form.avatar.data
            new_avatar.stream.seek(0)
            filename = secure_filename(new_avatar.filename)
            ext = os.path.splitext(filename)[1]
            avatar_name = str(current_user.id) + ext
            avatar_path = os.path.join(current_app.instance_path, 'uploads', 'avatar', avatar_name)
            if current_user.avatar:
                old_avatar_path = os.path.join(current_app.instance_path, 'uploads', 'avatar', current_user.avatar)
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            new_avatar.save(avatar_path)
            current_user.avatar = avatar_name

        if isinstance(form.banner.data, FileStorage):
            new_banner = form.banner.data
            new_banner.stream.seek(0)
            filename = secure_filename(new_banner.filename)
            ext = os.path.splitext(filename)[1]
            banner_name = str(current_user.id) + ext
            banner_path = os.path.join(current_app.instance_path, 'uploads', 'banner', banner_name)
            if current_user.banner:
                old_banner_path = os.path.join(current_app.instance_path, 'uploads', 'banner', current_user.banner)
                if os.path.exists(old_banner_path):
                    os.remove(old_banner_path)
            new_banner.save(banner_path)
            current_user.banner = banner_name

        db.session.commit()

        flash("Profile updated successfully.", "success")
        return redirect(url_for("user.user_edit"))

    return render_template("pages/user_edit.html", form=form)

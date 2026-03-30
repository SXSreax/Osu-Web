from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request
from flask_login import current_user, login_required
from app.models import db, BeatmapDiff, User
from app.forms import UserEditForm
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os
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

        beatmap_card.append({
            'id': bms.id,
            'name': bms.name,
            'artist': bms.artist,
            'uploader': bms.uploader,
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
            'user': {
                'name': user.username if user else "Unknown",
                'avatar': user.avatar if user else None
            }
        })

    return render_template("pages/user.html", beatmaps=beatmap_card, discussions=discussions)

@user_bp.route('/user/edit/', methods=["GET", "POST"])
@login_required
def user_edit():
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

        if not current_user.check_password(form.old_password.data):
            flash("Current password is incorrect.")
            return render_template("pages/user_edit.html", form=form)

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

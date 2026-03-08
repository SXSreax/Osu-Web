from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request
from flask_login import current_user, login_required
from app.models import db
from app.forms import UserEditForm
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/')
@login_required
def user():
    return render_template("pages/user.html")

@user_bp.route('/user/edit/', methods=["GET", "POST"])
@login_required
def user_edit():
    form = UserEditForm()

    if request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    if form.validate_on_submit():
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

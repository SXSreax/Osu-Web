from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, User
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from app.forms import LoginForm
from werkzeug.security import check_password_hash

login_bp = Blueprint('login', __name__)

@login_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_active:
        flash("Already logined in, logout first to relogin", "warning")
        return redirect(url_for('home.home'))
    form = LoginForm()
    if form.validate_on_submit():
        id = form.identity.data
        password = form.password.data
        
        user = User.query.filter_by(username=id).first()

        if not user:
            user = User.query.filter_by(email=id).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            # old login session
            # session['user_id'] = user.id
            # session['username'] = user.username
            flash("Login successfully", "success")
            return redirect(url_for('home.home'))
        
        else:
            flash("Invalid username or password.", "error")
    return render_template("pages/login.html", form=form)

@login_bp.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('home.home'))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from app.forms import UserForm
from werkzeug.security import generate_password_hash
import uuid

signup_bp = Blueprint('signup', __name__)

def check_id(user_id):
    return User.query.filter_by(id=user_id).first()

@signup_bp.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data.lower()
        password = form.password.data

        exist_username = User.query.filter_by(username=username).first()
        exist_email = User.query.filter_by(email=email).first()
        if exist_username:
            flash("username already existed", "warning")
            return redirect(url_for("signup.signup"))
        
        if exist_email:
            flash("email already existed", "warning")
            return redirect(url_for("signup.signup"))
        
        while True:
            user_id = str(uuid.uuid4())
            if not check_id(user_id):
                break

        hashed_password = generate_password_hash(password)
        new_user = User(id=user_id, username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash(f"User {username} created successfully", "success")
        return redirect(url_for("signup.signup"))
    return render_template('pages/signup.html', form=form)

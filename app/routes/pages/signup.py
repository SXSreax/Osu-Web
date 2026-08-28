from flask import Blueprint, render_template, redirect, url_for, flash
from app.models import db, User
from app.forms import UserForm
from werkzeug.security import generate_password_hash
import uuid

signup_bp = Blueprint('signup', __name__)


def check_id(user_id):
    # Return an existing row so signup can avoid UUID collisions.
    return User.query.filter_by(id=user_id).first()


@signup_bp.route('/signup/', methods=['GET', 'POST'])
def signup():
    """
    Register a new user account.

    Inputs:
        - GET: None
        - POST: signup form data for username, email, and password

    Processing:
        - Validate the form and check for duplicate username or email.
        - Create a new user account and hash the password.

    Outputs:
        - Renders the signup form or redirects to the login page after success.
    """
    form = UserForm()
    # Only query for duplicates after all submitted fields are valid.
    if form.validate_on_submit():
        # Collect the submitted account details.
        username = form.username.data
        # Normalize the email so duplicate checks and logins stay consistent.
        email = form.email.data.lower()
        password = form.password.data

        # Check whether the username or email already exists.
        # Check both unique account identifiers before inserting a user.
        exist_username = User.query.filter_by(username=username).first()
        exist_email = User.query.filter_by(email=email).first()
        # Redirect back so the user can choose a different username.
        if exist_username:
            flash("username already existed", "warning")
            return redirect(url_for("signup.signup"))

        # Redirect back so the user can choose a different email address.
        if exist_email:
            flash("email already existed", "warning")
            return redirect(url_for("signup.signup"))

        while True:
            # Keep generating IDs until an unused UUID is found.
            user_id = str(uuid.uuid4())
            # Stop once the generated UUID is absent from the database.
            if not check_id(user_id):
                break

        hashed_password = generate_password_hash(password)
        new_user = User(id=user_id,
                        username=username,
                        email=email,
                        password=hashed_password)
        # Stage and commit the new account with its hashed password.
        db.session.add(new_user)
        db.session.commit()
        flash(f"User {username} created successfully, please login", "success")
        return redirect(url_for("login.login"))
    return render_template('pages/signup.html', form=form)

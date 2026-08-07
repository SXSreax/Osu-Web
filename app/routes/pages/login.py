from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
from app.forms import LoginForm
from werkzeug.security import check_password_hash

login_bp = Blueprint('login', __name__)


@login_bp.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Handle user login and authentication.

    Inputs:
        - GET: None
        - POST: username or email and password from the form

    Processing:
        - Check whether the user is already logged in.
        - Validate the submitted credentials.
        - Log the user in on success.

    Outputs:
        - Renders the login page or redirects to the home page.
    """
    if current_user.is_active:
        # Redirect authenticated users away from the login page to
        # prevent duplicate sessions.
        flash("Already logined in, logout first to relogin", "warning")
        return redirect(url_for('home.home'))
    form = LoginForm()
    if form.validate_on_submit():
        # Collect the submitted login credentials.
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
    """
    Log the current user out of the session.

    Inputs:
        - GET: None

    Processing:
        - Clear the authenticated session and reset the settings flag.

    Outputs:
        - Redirects the user back to the home page.
    """
    logout_user()
    # Reset the verification flag so the next login starts from a clean state.
    session["settings_verified_until"] = 0
    flash("Logged out successfully.", "success")
    return redirect(url_for('home.home'))

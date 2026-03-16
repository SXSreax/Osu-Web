from flask import Blueprint, render_template, current_app

error_bp = Blueprint('error', __name__)

@error_bp.app_errorhandler(401)
def unauthorized(e):
    code = "401"
    error_message = "Unauthorized login, you will need an account"
    soln = "Login or signup in to continue"
    return render_template("error/error.html", error_message=error_message, code=code, soln=soln), 401
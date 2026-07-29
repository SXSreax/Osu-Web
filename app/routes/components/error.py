from flask import Blueprint, render_template, current_app

error_bp = Blueprint('error', __name__)

@error_bp.app_errorhandler(401)
def unauthorized(e):
    code = "401"
    error_message = "Unauthorized login, you will need an account"
    soln = "Login or signup in to continue"
    return render_template("error/401.html", error_message=error_message, code=code, soln=soln), 401

@error_bp.app_errorhandler(404)
def not_found(e):
    code = "404"
    error_message = "Page not found"
    soln = "Redirct to home page"
    return render_template("error/404.html", error_message=error_message, code=code, soln=soln), 404
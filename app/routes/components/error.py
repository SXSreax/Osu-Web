from flask import Blueprint, render_template

error_bp = Blueprint('error', __name__)


@error_bp.app_errorhandler(401)
def unauthorized(e):
    # Set error details for the 401 page
    # Return the HTTP status so clients know authentication is required.
    code = "401"
    error_message = "Unauthorized login, you will need an account"
    soln = "Login or signup in to continue"
    return render_template("error/401.html",
                           error_message=error_message,
                           code=code,
                           soln=soln), 401


@error_bp.app_errorhandler(404)
def not_found(e):
    # Set error details for the 404 page
    # Render a consistent page for routes or files that cannot be found.
    code = "404"
    error_message = "Page not found"
    soln = "Redirct to home page"
    return render_template("error/404.html",
                           error_message=error_message,
                           code=code,
                           soln=soln), 404

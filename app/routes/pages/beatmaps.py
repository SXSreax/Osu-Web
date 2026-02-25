from flask import Blueprint, render_template

beatmaps_bp = Blueprint('beatmaps', __name__)

@beatmaps_bp.route('/')
def beatmaps():
    return render_template('pages/home.html')

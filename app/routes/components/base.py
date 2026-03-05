from flask import Blueprint, render_template, current_app, send_file
from flask_login import current_user
from app.models import User
import os

base_bp = Blueprint('base', __name__)

@base_bp.app_context_processor
def user_info():
    return dict(logged_in_user=current_user)

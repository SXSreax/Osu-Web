from flask import Blueprint
from app.utils.files import serve_instance_file
import os

base_bp = Blueprint('base', __name__)

@base_bp.route('/uploads/avatar/<path:filename>')
def avatar(filename):
    filepath = os.path.join('uploads', 'avatar', filename)
    return serve_instance_file(filepath)
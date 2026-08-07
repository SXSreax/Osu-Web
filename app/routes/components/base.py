from flask import Blueprint
from app.utils.files import serve_instance_file
import os

base_bp = Blueprint('base', __name__)


@base_bp.route('/uploads/avatar/<path:filename>')
def avatar(filename):
    # Build the instance-relative upload path so avatar files can be
    # served safely.
    filepath = os.path.join('uploads', 'avatar', filename)
    return serve_instance_file(filepath)


@base_bp.route('/uploads/banner/<path:filename>')
def banner(filename):
    # Build the instance-relative upload path so banner files can be
    # served safely.
    filepath = os.path.join('uploads', 'banner', filename)
    return serve_instance_file(filepath)

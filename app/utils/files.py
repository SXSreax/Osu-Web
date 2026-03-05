import os
from flask import current_app, send_file

def serve_instance_file(filepath):
    instance_path = current_app.instance_path
    file_path = os.path.join(instance_path, filepath)

    if not os.path.abspath(file_path).startswith(os.path.abspath(instance_path)):
        return 'Forbidden', 403

    if os.path.isfile(file_path):
        return send_file(file_path)

    return 'Not Found', 404
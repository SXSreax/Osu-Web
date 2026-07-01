from flask_socketio import SocketIO
from flask_mail import Mail

socketio = SocketIO(cors_allowed_origins="*")
mail = Mail()

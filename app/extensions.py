from flask_socketio import SocketIO
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

socketio = SocketIO(cors_allowed_origins="*")
mail = Mail()
db = SQLAlchemy()

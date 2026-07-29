from flask import Flask
from app.models import db, User
from app.extensions import socketio, mail
from dotenv import load_dotenv
from config import Config
import os
from flask_login import LoginManager
from app.routes.pages.home import home_bp as home
from app.routes.pages.beatmaps import beatmaps_bp as beatmaps
from app.routes.pages.map import map_bp as map
from app.routes.pages.upload import upload_bp as upload
from app.routes.pages.signup import signup_bp as signup
from app.routes.pages.login import login_bp as login
from app.routes.pages.user import user_bp as user
from app.routes.pages.community import community_bp as community
from app.routes.pages.discussion import discussion_bp as discussion
from app.routes.pages.user_hub import user_hub_bp as user_hub
from app.routes.components.base import base_bp as base
from app.routes.components.error import error_bp as error

login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    #set up environment keys
    load_dotenv(".secrets")
    app.config['TOTP_KEY'] = os.getenv("KEY")

    #config
    app.config["OSU_CLIENT_ID"] = os.getenv("OSU_CLIENT_ID")
    app.config["OSU_CLIENT_SECRET"] = os.getenv("OSU_CLIENT_SECRET")
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['AVATAR_FOLDER'] = Config.AVATAR_FOLDER
    app.config['BANNER_FOLDER'] = Config.BANNER_FOLDER
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['DEBUG'] = Config.DEBUG
    app.config["MAIL_SERVER"] = Config.MAIL_SERVER
    app.config["MAIL_PORT"] = Config.MAIL_PORT
    app.config["MAIL_USE_TLS"] = Config.MAIL_USE_TLS
    app.config["MAIL_USE_SSL"] = Config.MAIL_USE_SSL
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)
    os.makedirs(app.config['BANNER_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path, 'temp_uploads'), exist_ok=True)

    # Initialization
    db.init_app(app)
    mail.init_app(app)

    login_manager.init_app(app)
    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # Register blueprints
    app.register_blueprint(home)
    app.register_blueprint(beatmaps)
    app.register_blueprint(map)
    app.register_blueprint(upload)
    app.register_blueprint(signup)
    app.register_blueprint(login)
    app.register_blueprint(user)
    app.register_blueprint(community)
    app.register_blueprint(discussion)
    app.register_blueprint(user_hub)
    app.register_blueprint(base)
    app.register_blueprint(error)

    socketio.init_app(app)
    return app

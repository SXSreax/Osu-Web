from flask import Flask
from app.models import db, User
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
    app.config['SECRET_KEY'] = 'dont-hack-me'
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'flaskr.sqlite')
    app.config['AVATAR_FOLDER'] = os.path.join(app.instance_path, 'uploads', 'avatar')
    app.config['BANNER_FOLDER'] = os.path.join(app.instance_path, 'uploads', 'banner')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)
    os.makedirs(app.config['BANNER_FOLDER'], exist_ok=True)
    
    # Initialize database with app
    db.init_app(app)

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
    
    return app

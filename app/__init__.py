from flask import Flask
from app.models import db
import os

from app.routes.pages.home import home_bp as home
from app.routes.pages.beatmaps import beatmaps_bp as beatmaps
from app.routes.pages.map import map_bp as map
from app.routes.pages.upload import upload_bp as upload
from app.routes.pages.signup import signup_bp as signup
from app.routes.pages.login import login_bp as login

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'dont-hack-me'
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'flaskr.sqlite')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads', 'avatar')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database with app
    db.init_app(app)

    with app.app_context():
        db.create_all()
    
    # Register blueprints
    app.register_blueprint(home)
    app.register_blueprint(beatmaps)
    app.register_blueprint(map)
    app.register_blueprint(upload)
    app.register_blueprint(signup)
    app.register_blueprint(login)
    
    return app

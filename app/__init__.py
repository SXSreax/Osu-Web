from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

from app.routes.pages.home import home_bp as home

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'flaskr.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    
    # Initialize database with app
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(home)
    
    return app

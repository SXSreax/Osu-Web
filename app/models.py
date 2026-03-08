from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import uuid

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    banner = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

    def get_id(self):
        return str(self.id)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Beatmap(db.Model):
    __tablename__ = 'beatmaps'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    artist = db.Column(db.String(255), nullable=True)
    uploader = db.Column(db.String(120), nullable=True)
    filepath = db.Column(db.String(1024), nullable=False)

    def __repr__(self):
        return f'<Beatmap {self.id} {self.artist} - {self.name}>'


class BeatmapDiff(db.Model):
    __tablename__ = 'beatmaps_diff'

    id = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.Integer, db.ForeignKey('beatmaps.id'), nullable=False)
    map_name = db.Column(db.String(255), nullable=False)
    star_diff = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<BeatmapDiff {self.map_id} - {self.map_name} ({self.star_diff})>'
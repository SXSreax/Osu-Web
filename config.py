import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'database.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'dont-hack-me'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'flaskr.sqlite')
    AVATAR_FOLDER = os.path.join(BASE_DIR, 'instance', 'uploads', 'avatar')
    BANNER_FOLDER = os.path.join(BASE_DIR, 'instance', 'uploads', 'banner')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT =587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False


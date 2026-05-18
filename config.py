import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY     = os.environ.get("SECRET_KEY", "cambia-esto-en-produccion")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)

JWT_ACCESS_TOKEN_EXPIRES  = timedelta(minutes=60)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://root:@localhost/citas_romanticas2",
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
AUTH_ROLE_ADMIN = 'Admin'

AUTH_ROLE_PUBLIC = 'Public'
# Setup default language
BABEL_DEFAULT_LOCALE = "en"
# Your application default translation path
BABEL_DEFAULT_FOLDER = "translations"
# The allowed translation for you app
LANGUAGES = {
    "en": {"flag": "gb", "name": "English"},
    "pt": {"flag": "pt", "name": "Portuguese"},
    "pt_BR": {"flag": "br", "name": "Pt Brazil"},
    "es": {"flag": "es", "name": "Spanish"},
    "de": {"flag": "de", "name": "German"},
    "zh": {"flag": "cn", "name": "Chinese"},
    "ru": {"flag": "ru", "name": "Russian"},
    "pl": {"flag": "pl", "name": "Polish"},
}

IMG_UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads") + os.sep
IMG_UPLOAD_URL    = "/static/uploads/"
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
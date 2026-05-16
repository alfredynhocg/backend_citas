import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY     = os.environ.get("SECRET_KEY", "cambia-esto-en-produccion")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)

JWT_ACCESS_TOKEN_EXPIRES  = timedelta(minutes=15)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://root:@localhost/citas_romanticas",
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

IMG_UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads") + os.sep
IMG_UPLOAD_URL    = "/static/uploads/"
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:4200").split(",")

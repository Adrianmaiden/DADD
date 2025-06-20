import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "mi_clave_secreta")
    DEBUG = True

    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')

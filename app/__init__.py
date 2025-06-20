from flask import Flask
from .extensions import login_manager
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)
    load_dotenv()

    # Configuración básica
    app.secret_key = os.getenv('SECRET_KEY', 'secret-key-default')

    # Inicializar extensiones
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'

    # Registrar blueprints
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    return app
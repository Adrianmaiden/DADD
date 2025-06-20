from flask import Blueprint, render_template, redirect, url_for, session, flash
from flask_login import current_user


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Si el usuario ya está autenticado, llévalo directamente al dashboard
    # para una mejor experiencia de usuario.
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Si no, muestra la página de inicio normal.
    return render_template('index.html')
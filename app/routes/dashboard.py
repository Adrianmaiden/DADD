# app/routes/dashboard.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.db import get_db_connection, close_db_connection
import traceback 
import os
from werkzeug.utils import secure_filename

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    datasets = []
    actividad = []
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Consulta de Datasets
        cursor.execute("""
            SELECT id, nombre, tipo, fecha_creacion 
            FROM datasets 
            WHERE usuario_id = %s
            ORDER BY fecha_creacion DESC LIMIT 5
        """, (current_user.id,))
        datasets = cursor.fetchall()
        
        # Consulta de Actividad
        cursor.execute("""
            SELECT tipo_accion, fecha 
            FROM actividad 
            WHERE usuario_id = %s
            ORDER BY fecha DESC LIMIT 5
        """, (current_user.id,))
        actividad = cursor.fetchall()

    except Exception as e:
        # --- ¡ESTA ES LA PARTE IMPORTANTE! ---
        # Imprime el error completo en la terminal para que puedas verlo.
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!!         ERROR EN EL DASHBOARD             !!!")
        print(f"!!! Error: {e}")
        print("!!! Traceback:")
        traceback.print_exc() # Imprime la traza completa del error
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        
        # Muestra un mensaje flash más informativo al usuario
        flash('Hubo un error crítico al cargar el dashboard. Se ha notificado al administrador.', 'danger')
        # Redirigir al index sigue siendo un buen plan B
        return redirect(url_for('main.index'))
        
    finally:
        close_db_connection(conn, cursor)

    return render_template('dashboard.html', 
                           current_user=current_user,
                           datasets=datasets,
                           actividad=actividad)

@dashboard_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    # 1. Verificar si el archivo está en la solicitud
    if 'dataFile' not in request.files:
        flash('No se encontró el campo del archivo en el formulario.', 'danger')
        return redirect(url_for('dashboard.index'))

    file = request.files['dataFile']

    # 2. Verificar si el usuario no seleccionó ningún archivo
    if file.filename == '':
        flash('No se seleccionó ningún archivo para subir.', 'warning')
        return redirect(url_for('dashboard.index'))

    # 3. Si el archivo existe y es válido
    if file:
        # Asegurar el nombre del archivo para evitar problemas de seguridad
        filename = secure_filename(file.filename)
        
        # Crear la ruta completa para guardar el archivo
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        try:
            # Guardar el archivo en el servidor
            file.save(save_path)
            
            # (PRÓXIMO PASO): Aquí iría la lógica para leer el archivo con pandas
            # y guardar los datos en la base de datos.
            # pd.read_csv(save_path) o pd.read_excel(save_path) ...
            
            flash(f'Archivo "{filename}" subido exitosamente. ¡Listo para procesar!', 'success')
        except Exception as e:
            flash(f'Hubo un error al guardar el archivo: {str(e)}', 'danger')

    return redirect(url_for('dashboard.index'))
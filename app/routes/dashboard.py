# app/routes/dashboard.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.db import get_db_connection, close_db_connection
import traceback 
import os
from werkzeug.utils import secure_filename
import pandas as pd

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

@dashboard_bp.route('/api/v1/upload', methods=['POST'])
@login_required
def api_upload_file():
    if 'dataFile' not in request.files:
        return jsonify({"error": "No se encontró el campo del archivo."}), 400

    file = request.files['dataFile']
    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400

    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(save_path)
            # Llamamos a la función que procesa el archivo y devuelve un resultado
            success, message = process_datafile(save_path, filename)
            
            if success:
                # Si el procesamiento fue exitoso, devolvemos un JSON de éxito
                return jsonify({"message": message}), 201 # 201 Created
            else:
                # Si el procesamiento falló, devolvemos un JSON de error
                return jsonify({"error": message}), 500 # 500 Internal Server Error

        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": f"Error crítico al guardar el archivo: {e}"}), 500

    return jsonify({"error": "Ocurrió un error inesperado."}), 500

# --- FUNCIÓN DE LÓGICA DE PROCESAMIENTO (Separada y Limpia) ---
def process_datafile(file_path, original_filename):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.start_transaction()

        file_extension = original_filename.split('.')[-1].lower()
        
        sql_create_dataset = "INSERT INTO datasets (usuario_id, nombre, tipo, formato_original, ruta_archivo, columnas_config) VALUES (%s, %s, %s, %s, %s, '{}')"
        cursor.execute(sql_create_dataset, (current_user.id, original_filename, 'finanzas', file_extension, file_path))
        dataset_id = cursor.lastrowid

        if file_extension == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            sql_insert_data = "INSERT INTO datos_finanzas (dataset_id, fecha, descripcion, monto, categoria) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql_insert_data, (
                dataset_id, pd.to_datetime(row['Fecha']).strftime('%Y-%m-%d'), row['Descripcion'], float(row['Monto']), row['Categoria']
            ))
        
        conn.commit()
        return True, f"Archivo '{original_filename}' procesado y {len(df)} registros guardados."

    except Exception as e:
        if conn:
            conn.rollback()
        traceback.print_exc()
        return False, f"Error en el procesamiento de datos: {e}"
    finally:
        close_db_connection(conn, cursor)
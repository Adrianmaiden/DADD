from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from flask_login import login_user, logout_user, current_user
import bcrypt
from app.models.user import User
from app.db import get_db_connection, close_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['contraseña']
        
        print("\n--- INICIO DE INTENTO DE LOGIN ---")
        print(f"Usuario recibido: {username}")

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            print("1. Conectado a la BD. Buscando usuario...")
            cursor.execute("SELECT id, username, password_hash, rol FROM usuarios WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            
            if user_data:
                print(f"2. Usuario encontrado en la BD: {user_data['username']}")
                print("3. Verificando contraseña...")

                # Verificación de la contraseña
                password_is_correct = bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash'].encode('utf-8'))

                if password_is_correct:
                    print("4. ¡CONTRASEÑA CORRECTA! Creando objeto User y haciendo login.")
                    user = User(
                        id=user_data['id'],
                        username=user_data['username'],
                        password_hash=user_data['password_hash'],
                        rol=user_data['rol']
                    )
                    login_user(user)
                    print("5. Redirigiendo a 'dashboard.index'...")
                    return redirect(url_for('dashboard.index'))
                else:
                    print("4. ¡CONTRASEÑA INCORRECTA!")
                    flash('Usuario o contraseña incorrectos.', 'danger')
            else:
                print("2. Usuario NO encontrado en la BD.")
                flash('Usuario o contraseña incorrectos.', 'danger')
            
        except Exception as e:
            print(f"!!! OCURRIÓ UNA EXCEPCIÓN: {str(e)} !!!")
            flash(f'Error de sistema: {str(e)}', 'danger')
        finally:
            close_db_connection(conn, cursor)
    
    print("--- FIN DE INTENTO DE LOGIN: Renderizando de nuevo la página de login. ---")
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre_completo = request.form.get('nombre_completo')
        username = request.form.get('usuario')
        email = request.form.get('email')
        password = request.form.get('contraseña')

        if not all([nombre_completo, username, email, password]):
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Verificar si el usuario o email ya existen para evitar duplicados
            cursor.execute("SELECT id FROM usuarios WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                flash('El nombre de usuario o el correo ya están en uso.', 'warning')
                return redirect(url_for('auth.register'))

            # Insertar el nuevo usuario con el rol 'usuario' por defecto
            sql = """
                INSERT INTO usuarios (nombre_completo, username, email, password_hash, rol, esta_activo)
                VALUES (%s, %s, %s, %s, 'usuario', TRUE)
            """
            values = (nombre_completo, username, email, hashed_password)
            cursor.execute(sql, values)
            conn.commit()

            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f'Ocurrió un error en el servidor: {e}', 'danger')
            if conn:
                conn.rollback()
            return redirect(url_for('auth.register'))
        finally:
            close_db_connection(conn, cursor)

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('main.index'))
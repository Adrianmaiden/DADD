# DADD/seed_db.py

import bcrypt
from app.db import get_db_connection, close_db_connection
import os

def seed_users():
    """
    Inserta un usuario administrador y un cliente de prueba si no existen.
    Los roles ('admin', 'usuario') coinciden con la BD.
    """
    users_to_add = [
        {
            "username": "admin",
            "password": "admin_password", # Cambia esto por una contraseña segura
            "rol": "admin",
            "email": "admin@dadd.com",
            "nombre_completo": "Administrador Principal"
        },
        {
            "username": "cliente",
            "password": "cliente_password", # Cambia esto por una contraseña segura
            "rol": "usuario", # El rol 'cliente' en la lógica es 'usuario' en la BD
            "email": "cliente@dadd.com",
            "nombre_completo": "Cliente de Prueba"
        }
    ]

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for user_data in users_to_add:
            # Verificar si el usuario ya existe
            cursor.execute("SELECT id FROM usuarios WHERE username = %s", (user_data["username"],))
            if cursor.fetchone():
                print(f"✅ El usuario '{user_data['username']}' ya existe.")
                continue

            # Hashear la contraseña
            password = user_data["password"].encode('utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

            # Insertar el nuevo usuario
            sql = """
                INSERT INTO usuarios (username, email, password_hash, nombre_completo, rol, esta_activo)
                VALUES (%s, %s, %s, %s, %s, TRUE)
            """
            values = (
                user_data["username"],
                user_data["email"],
                hashed_password,
                user_data["nombre_completo"],
                user_data["rol"]
            )
            cursor.execute(sql, values)
            print(f"🚀 Usuario '{user_data['username']}' creado exitosamente.")

        conn.commit()

    except Exception as e:
        print(f"❌ Error al insertar usuarios iniciales: {e}")
        if conn:
            conn.rollback()
    finally:
        close_db_connection(conn, cursor)

if __name__ == "__main__":
    seed_users()
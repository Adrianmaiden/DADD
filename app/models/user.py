from flask_login import UserMixin
from app.db import get_db_connection

class User(UserMixin):
    def __init__(self, id, username, password_hash, rol):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.rol = rol

    @staticmethod
    def get(user_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT id, username, password_hash, rol FROM usuarios WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            
            if user_data:
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    rol=user_data['rol']
                )
            return None
            
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

# Nota: El user_loader se configurará en extensions.py
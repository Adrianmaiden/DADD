import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'root'),
            database=os.getenv('DB_NAME', 'dadd_db')
        )
        if connection.is_connected():
            print("✅ Conexión exitosa a MySQL")
            return connection
    except Error as e:
        print(f"❌ Error al conectar a MySQL: {e}")
        raise

def close_db_connection(connection, cursor=None):
    try:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("🔌 Conexión cerrada")
    except Error as e:
        print(f"⚠️ Error al cerrar conexión: {e}")
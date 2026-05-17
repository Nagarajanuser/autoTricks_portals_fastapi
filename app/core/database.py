import mysql.connector
from mysql.connector import Error
from .config import settings

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
            port=settings.MYSQL_PORT
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def get_db_cursor():
    conn = get_db_connection()
    if conn:
        return conn, conn.cursor(dictionary=True)
    return None, None

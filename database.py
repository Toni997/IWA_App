import mysql.connector
import os

USERNAME = 'root'
PASSWORD = os.getenv('SQL_PASSWORD', 'root')
HOST = 'localhost'
DB_NAME = 'iwa'

config = {
    'user': USERNAME,
    'password': PASSWORD,
    'host': HOST,
    'database': DB_NAME
}

db = mysql.connector.connect(**config)
cursor = db.cursor(dictionary=True)

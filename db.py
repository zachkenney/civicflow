import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    database=os.getenv('db_name'),
    password=os.getenv('password'),
    user=os.getenv('user'),
    port=os.getenv('port'),
    host=os.getenv('host'),
    client_encoding='utf8'
)

def connect():
    try:
        cursor = conn.cursor()
        print('Connection to database successful.')
    except Exception:
        print('Unable to connect to database.')
    return cursor
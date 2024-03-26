import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def pgsql_connect():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"), 
            user=os.getenv("DB_USERNAME"), 
            password=os.getenv("DB_PASSWORD"), 
            host=os.getenv("DB_HOST"), 
            port=os.getenv("DB_PORT") 
        )
        print("Connected to the database.")

        return conn 
    
    
    except Exception as e:
        print(f"Unable to connect to the database: {e}")

connection = pgsql_connect()
cur = connection.cursor()
# db.py
import psycopg2
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()
# Function to create a PostgreSQL connection
def create_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="paperpalooza",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port="5432"
        )
        st.success("Connected to PostgreSQL database.")
        return conn
    except psycopg2.Error as e:
        st.error(f"Error connecting to PostgreSQL database: {e}")
        return None

# Function to execute a query
def execute_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        st.success("Query executed successfully.")
    except psycopg2.Error as e:
        st.error(f"Error executing query: {e}")

# Function to close the connection
def close_connection(conn):
    try:
        if conn is not None:
            conn.close()
            st.success("Connection to PostgreSQL database closed.")
    except psycopg2.Error as e:
        st.error(f"Error closing connection: {e}")

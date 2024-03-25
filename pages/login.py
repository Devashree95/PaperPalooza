import streamlit as st
from db import create_connection, execute_query, close_connection
import bcrypt

def main():

    conn = create_connection()
    st.title("Login Page")

    # Create placeholders for username and password input
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Check if the login button is clicked
    if st.button("Login"):
       login(username, password, conn)
    
    if st.button("Sign Up"):
        signup(username, password, conn)

def login(username, password, conn):
    query = f"SELECT password FROM users WHERE email = '{username}'"
    bytes = password.encode('utf-8')
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.commit()
    hash = rows[0][0]
    hash = hash.encode()
    result = bcrypt.checkpw(bytes, hash)
    if result:
        st.success("LOGGED IN!")
        if 'auth' not in st.session_state:
            st.session_state['auth'] = True
            # st.session_state['user'] = username
            st.switch_page("pages/ScholarySearch.py")
    else:
        st.error("NOPE!")
    

def signup(username, password, conn):
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    hash = hash.decode('utf-8')

    query = f"INSERT INTO users (email, password, usertype) VALUES ('{username}', '{hash}', 'researcher')"
    
    execute_query(conn, query)
    st.success("User signed up successfully")

if __name__ == "__main__":
    main()

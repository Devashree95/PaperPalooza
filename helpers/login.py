import streamlit as st
from helpers import connection as conn
import bcrypt
import uuid


connection = conn.pgsql_connect()
cur = connection.cursor()

st.session_state['button_clicked'] = st.session_state.get('button_clicked', False)

if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

def handle_click():
    st.session_state.button_clicked = True
    st.session_state.show_login = False  # Hide login form and show account creation form

def login_snippet(key="login"):
    st.session_state['button_clicked'] = st.session_state.get('button_clicked', False)
    if "user_logged_in" not in st.session_state:
        st.session_state.user_logged_in = False
    
    if "show_login" not in st.session_state:
        st.session_state.show_login = True  # By default, show the login form

    # Create an empty container for dynamic forms
    placeholder = st.empty()

    if not st.session_state.user_logged_in:
        if st.session_state.show_login:

            # Insert a form in the container
            with placeholder.form(key=key):
                st.markdown("#### Enter your credentials")
                email = st.text_input("Email")
                input_password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Log In")


            if submit:
                st.session_state['username'] = email
                # If submit, check if the email exists in the database
                try:
                    cur.execute("SELECT EXISTS (SELECT 1 FROM users WHERE username = %s)", (email,))
                    email_exists = cur.fetchone()
                    if not email_exists[0]:
                        st.toast("Invalid username")
                        st.stop()

                    # If submit, fetch password from the database
                    cur.execute("SELECT password, role FROM users WHERE username = %s", (email,))
                    data = cur.fetchone()
                    password = data[0]
                    role = data[1]
                    
                    bytes = input_password.encode('utf-8')
                    hash = password
                    hash = hash.encode()
                    result = bcrypt.checkpw(bytes, hash)
                    if result:
                        st.toast("Login successful")
                        st.session_state.user_logged_in = True
                        st.session_state['role'] = role
                        if "username" not in st.session_state:
                            st.session_state.username = email
                        placeholder.empty()  # Clear the form
                        # You can redirect or continue execution here since the user is logged in
                        return True

                    else:
                        st.toast("Login failed, incorrect password")
                        st.stop()
                
                except Exception as e:
                    st.error(f"Error: {e}")
                    print(f"Error: {e}")
                    st.stop()

            if not st.session_state.button_clicked:
                create_account_button = st.button("Create new account", on_click=handle_click)
                if create_account_button:
                    st.session_state.button_clicked = True
                    st.session_state.show_login = False  # Hide login form and show account creation form
                    placeholder.empty()  # Clear the existing form in the placeholder

        if not st.session_state.show_login:  # This means st.session_state.show_login is False, so show the account creation form
            with placeholder.form(key="create_account_form"):
                st.markdown("#### Enter your credentials to create a new account")
                new_email = st.text_input("Email", key="new_email")  # Use unique key for new form
                new_password = st.text_input("Password", type="password", key="new_password")  # Use unique key
                name = st.text_input("Name", key="name")
                advisor = st.checkbox("Are you an advisor?")
                parts = name.split(' ')
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else '' 
                submit_account = st.form_submit_button("Create Account")
                
            if st.button("Cancel"):
                # Reset the relevant session states to display the login form again
                st.session_state.show_login = True
                st.session_state.button_clicked = False
                st.rerun()

            if submit_account:
                bytes = new_password.encode('utf-8')
                salt = bcrypt.gensalt()
                hash = bcrypt.hashpw(bytes, salt)
                hash = hash.decode('utf-8')
                role = "researcher"
                if advisor:
                    role = "advisor"
                # Add role to execute query

                try:
                    cur.execute("INSERT INTO users (username, password, name, role) VALUES (%s, %s, %s, %s)", (new_email, hash, name, role))
                    user_id = uuid.uuid4()
                except Exception as e:
                    st.error(f"Error: {e}")
                    print(f"Error: {e}")
                    st.stop()

                try:
                    cur.execute("INSERT INTO users_v2 (username, password, name) VALUES (%s, %s, %s)", (new_email, hash, name))
                    cur.execute(f"insert into user_details values('{user_id}','{first_name}', '{last_name}', '{new_email}', Null , '', '{role}' )")
                    connection.commit()
                    st.toast("Account created successfully")
                    st.session_state['username'] = new_email
                    st.session_state['role'] = role
                    placeholder.empty()
                    st.session_state.user_logged_in = True
                    st.rerun()
                    return True
                    # st.session_state.show_login = True
                    # placeholder.empty()
                except Exception as e:
                    st.error(f"Error: {e}")
                    print(f"Error: {e}")
                    st.stop()

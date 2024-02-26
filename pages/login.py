import streamlit as st

def main():
    st.title("Login Page")

    # Create placeholders for username and password input
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Check if the login button is clicked
    if st.button("Login"):
       login()
    
    if st.button("Sign Up"):
        signup()

def login():
    pass

def signup():
    pass

if __name__ == "__main__":
    main()

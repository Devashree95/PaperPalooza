import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import os
from dotenv import load_dotenv


load_dotenv()

# Your Google OAuth 2.0 client ID and client secret
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SCOPES = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"]
REDIRECT_URI = "http://localhost:8501/login"

st.subheader("Sign in with Google")

# Create the authorization flow
flow = Flow.from_client_secrets_file(
    "client_secret.json", scopes=SCOPES, redirect_uri=REDIRECT_URI)

# Generate the authorization URL
authorization_url, _ = flow.authorization_url(
    access_type='offline', include_granted_scopes='true')

query_params = st.experimental_get_query_params()
code = query_params.get('code')

if code:
    flow.fetch_token(code=code)

    # Get user info
    user_info = flow.credentials.id_token
    st.write("User Info:", user_info)

# Display the login button
if st.button("Sign in with Google"):
    # Redirect to Google's login page
    st.markdown(f"[Sign in with Google]({authorization_url})")

    # Handle the callback after successful authentication



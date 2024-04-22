import streamlit as st
import helpers.sidebar
from PIL import Image
import base64
import bcrypt

from helpers import connection as conn


logo = "./images/profile_3135715.png"
image = Image.open(logo)

connection = conn.pgsql_connect()
cur = connection.cursor()

    # Function to convert image to Base64
def get_image_as_base64(path):
    with open(path, "rb") as image_file:
        data = base64.b64encode(image_file.read()).decode()
        return f"data:image/jpeg;base64,{data}"
        
def get_base64_of_file(path):
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode()
        
def set_background_from_local_file(path):
    base64_string = get_base64_of_file(path)
    # CSS to utilize the Base64 encoded string as a background
    css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{base64_string}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)
        
set_background_from_local_file('./images/grammar_background.png')
        
        
        
image_base64 = get_image_as_base64(logo)

st.markdown(f"""
                <a href="/" style="color:white;text-decoration: none;">
                    <div style="display:table;margin-top:-15 rem;margin-left:0%; display: flex;">
                        <img src="{image_base64}" alt="Insurehub Logo" style="width:50px;height:40px;margin-left:750px; flex:2;" </img>
                        <span style="padding:10px; flex:2;">{st.session_state.username}</span>
                    </div>
                </a>
                <br>
                    """, unsafe_allow_html=True)

cur.execute(f"select user_id from user_details where email = '{st.session_state['username']}'")
userId= cur.fetchall()[0][0]

def getProfileDetails(attr):
    cur.execute(f"select {attr} from user_details where user_id = '{userId}'")
    return cur.fetchall()[0][0]

def getPhoneDetails(attr):
    cur.execute(f"select phone from user_phone where user_id = '{userId}'")
    return cur.fetchall()

def updateDbTable(attr, val):
    print(val)
    if attr == 'phone1':
        cur.execute(f"update user_phone SET phone = '{val}' where user_id = '{userId}' and phone= '{phone_no_1}'")
        connection.commit()
    elif attr == 'phone2':
        if val == '':
            cur.execute(f"delete from user_phone where user_id = '{userId}' and phone= '{phone_no_2}'")
            connection.commit()

        if phone_no_2 == '':
            cur.execute(f"insert into user_phone VALUES ('{userId}','{val}')")
            connection.commit()
        else:
            cur.execute(f"update user_phone SET phone = '{val}' where user_id = '{userId}' and phone= '{phone_no_2}'")
            connection.commit()
    else:
        cur.execute(f"update user_details SET {attr} = '{val}' where user_id = '{userId}'")
        connection.commit()

phone_no = getPhoneDetails('phone')
if len(phone_no) == 1:
    phone_no_1 = phone_no[0][0]
    phone_no_2 = ''
elif len(phone_no) > 1:
    phone_no_1 = phone_no[0][0]
    phone_no_2 = phone_no[1][0]
else:
    phone_no_1 = ''
    phone_no_2 = ''

print("Phone 1 and phone 2 are", phone_no_1, phone_no_2)

profile = {
    "first_name": getProfileDetails('first_name'),
    "last_name": getProfileDetails('last_name'),
    "email": getProfileDetails('email'),
    "dob": getProfileDetails('dob'),
    "address": getProfileDetails('address'),
    "phone1": phone_no_1,
    "phone2": phone_no_2
}

def update_profile(first_name, last_name, email, dob, address, phone1, phone2):
    # Update profile data
    profile["first_name"] = first_name
    updateDbTable("first_name", first_name)
    profile["last_name"] = last_name
    updateDbTable("last_name", last_name)
    profile["email"] = email
    updateDbTable("email", email)
    profile["dob"] = dob
    updateDbTable("dob", dob)
    profile["address"] = address
    updateDbTable("address", address)
    profile["phone1"] = phone1
    updateDbTable("phone1", phone1)
    profile["phone2"] = phone2
    updateDbTable("phone2", phone2)
    st.success("Profile updated successfully!")

# Displaying the profile information
st.header("My Profile")

with st.form("profile_form"):
    first_name = st.text_input("First Name", value=profile["first_name"])
    last_name = st.text_input("Last Name", value=profile["last_name"])
    email = st.text_input("Email", value=profile["email"])
    dob = st.date_input("Date of Birth", value=profile["dob"])
    address = st.text_input("Address", value=profile["address"])
    phone1 = st.text_input("Phone 1", value=profile["phone1"])
    phone2 = st.text_input("Phone 2", value=profile["phone2"])
    
    # Form submission button
    submit_button = st.form_submit_button(label="Update Profile")
    
    if submit_button:
        update_profile(first_name, last_name, email, dob, address, phone1, phone2)

def change_password():
    with st.form(key='change_password_form'):
        st.markdown("#### Change your password")
        old_password = st.text_input("Enter your old password", type="password", key="old_password")
        new_password = st.text_input("Enter your new password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm your new password", type="password", key="confirm_password")
        submit_change = st.form_submit_button("Change Password")
        
    if submit_change:
        if new_password != confirm_password:
            st.error("New password and confirmation do not match.")
            return
        
        # Fetch the current hashed password from the database
        cur.execute("SELECT password FROM users WHERE username = %s", (st.session_state['username'],))
        current_hashed = cur.fetchone()[0]
        
        # Verify old password
        if bcrypt.checkpw(old_password.encode('utf-8'), current_hashed.encode('utf-8')):
            # Generate new hashed password
            new_bytes = new_password.encode('utf-8')
            new_salt = bcrypt.gensalt()
            new_hash = bcrypt.hashpw(new_bytes, new_salt).decode('utf-8')
            
            # Update the database with the new password
            try:
                cur.execute("UPDATE users SET password = %s WHERE username = %s", (new_hash, st.session_state['username']))
                connection.commit()
                st.success("Password changed successfully.")
            except Exception as e:
                st.error(f"Error updating password: {e}")
                print(f"Error updating password: {e}")
        else:
            st.error("Old password is incorrect.")

change_password()


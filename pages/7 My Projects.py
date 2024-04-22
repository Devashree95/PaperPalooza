import streamlit as st
import helpers.sidebar
from PIL import Image
import base64

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

def create_project(project_name, project_description, username):
    cur.execute("INSERT INTO Projects (title, description) VALUES (%s, %s) RETURNING id;", (project_name,project_description))
    project_id = cur.fetchone()[0]
    cur.execute("INSERT INTO userprojects (username, projectid) VALUES (%s, %s);", (username, project_id))
    connection.commit()
    cur.close()
        
        
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



# def get_projects_for_user():
username = st.session_state.username
# cur.execute("""SELECT * FROM projects JOIN UserProjects ON projects.id = UserProjects.projectID JOIN users on UserProjects.username = users.username WHERE users.username = %s;""", (username,))
cur.execute("""
            SELECT projects.title, projects.description, array_agg(users.username), projects.id
            FROM projects 
            JOIN userprojects ON projects.id = userprojects.projectid 
            JOIN users ON userprojects.username = users.username 
            GROUP BY projects.id, projects.title, projects.description;
        """)

projects = cur.fetchall()



st.title("Projects")

# projects = get_projects_for_user()
if projects:
    # st.table(projects)
    
    for project in projects:
        st.write("Title:", project[0])
        st.write("Description:", project[1])
        st.write("Users:", ", ".join(list(set(project[2]))))

        if st.session_state['role'] == 'advisor':
            new_username = st.text_input(f"Add username for project '{project[0]}':", key=f'userinput{project[3]}')
            if st.button(f"Add User", key=f'addbutton {project[3]}'):
                if new_username:
                    cur.execute("INSERT INTO userprojects (username, projectid) VALUES (%s, %s);", (new_username, project[3]))
                    connection.commit()
                    st.success(f"User '{new_username}' added to project '{project[0]}'.")
                else:
                    st.warning("Please enter a username.")
        st.write("---")
else:
    st.write("No Projects found for", username)


if st.session_state['role'] == 'advisor':

    st.header("Create new project")

    new_project_name = st.text_input("Enter project name:")
    new_project_description = st.text_area("Enter project description:")

    if st.button("Create Project"):
        if new_project_name:
            create_project(new_project_name, new_project_description, username)
            st.success(f"Created new project {new_project_name}")
        else:
            st.warning("Please enter a project name.")


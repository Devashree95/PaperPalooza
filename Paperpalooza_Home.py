import streamlit as st
import helpers.sidebar
from streamlit_option_menu import option_menu
from PIL import Image
import base64


st.set_page_config(
	page_title="Paperpalooza",
	page_icon="📄"
)

logo = "./images/profile_3135715.png"
image = Image.open(logo)


# Function to convert image to Base64
def get_image_as_base64(path):
    with open(path, "rb") as image_file:
        data = base64.b64encode(image_file.read()).decode()
        return f"data:image/jpeg;base64,{data}"
    
def get_base64_of_file(path):
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode()
	
image_base64 = get_image_as_base64(logo)

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
    
set_background_from_local_file('./images/background.png')

st.markdown(f"""
			<a href="/" style="color:white;text-decoration: none;">
				<div style="display:table;margin-top:-15 rem;margin-left:0%; display: flex;">
			  		<img src="{image_base64}" alt="PaperPalooza Logo" style="width:50px;height:40px;margin-left:750px; flex:2;" </img>
					<span style="padding:10px; flex:2;">Username</span>
				</div>
			</a>
			<br>
				""", unsafe_allow_html=True)

# selected2 = option_menu(None,	 ["My Profile"], 
#     icons=['gear'], 
#     menu_icon="cast", default_index=0, orientation="horizontal")


helpers.sidebar.show()

st.header("Welcome to Paperpalooza!")

st.subheader("Latest Research at Virginia Tech:")

video1_url = 'https://www.youtube.com/watch?v=5WyKVUtw90g'
video2_url = 'https://www.youtube.com/watch?v=ehn0aSEUJVM'
video3_url = 'https://www.youtube.com/watch?v=tAyQ9sUfPIo'
video4_url = 'https://www.youtube.com/watch?v=fCUqJeLl2to'

col1, col2 = st.columns(2)

with col1:
    st.video(video1_url)
    st.video(video3_url)
    
with col2:
    st.video(video2_url)
    st.video(video4_url)
    
st.subheader("Resources:")
st.markdown("[Virginia Tech Research Resources](https://www.research.vt.edu/research-development/resources.html)")

st.markdown("[Research Support](https://lib.vt.edu/research-teaching/research-services.html)")

st.markdown("[Virginia Tech Research](https://www.research.vt.edu/)")


    

    




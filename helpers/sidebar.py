import streamlit as st
from PIL import Image
import base64

logo = "./images/paperpalooza.png"
image = Image.open(logo)

# Function to convert image to Base64
def get_image_as_base64(path):
    with open(path, "rb") as image_file:
        data = base64.b64encode(image_file.read()).decode()
        return f"data:image/jpeg;base64,{data}"
	
image_base64 = get_image_as_base64(logo)

def show() -> None:
	with st.sidebar:
		st.markdown(f"""
			<a href="/" style="color:white;text-decoration: none;">
				<div style="display:table;margin-top:-14rem;margin-left:0%;">
			  		<img src="{image_base64}" alt="PaperPalooza Logo" style="width:50px;height:50px;margin-left:10px;" </img>
					<span>PaperPalooza</span>
					<span style="font-size: 0.8em; color: grey">&nbsp;&nbsp;v0.1.0</span>
				</div>
			</a>
			<br>
				""", unsafe_allow_html=True)
		

		# reload_button = st.button("↪︎  Reload Page")
		# if reload_button:
		# 	st.session_state.clear()
		# 	st.experimental_rerun()


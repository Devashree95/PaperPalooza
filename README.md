# Paperpalooza

Chech out our live demo [here](https://paperpalooza.discovery.cs.vt.edu/)

# Overview:
Paper Palooza is a forthcoming innovative web application planned to transform
the academic research process. The project will harness advanced AI technology
to create article summaries, integrate seamlessly with the arXiv API for extensive
paper search capabilities, integrate a research manager chatbot to assist the
students with their queries. Furthermore, the application will include a citation generator
supporting multiple formats and will incorporate user account functionality for a
personalized experience, facilitating research paper categorization and
management. Targeted at students, researchers, and academics, Paper Palooza
aims to simplify and enhance the efficiency of navigating the vast landscape of
academic literature

# Installation
Clone the Repository: git clone https://version.cs.vt.edu/kanadn/paperpalooza.git <br>
Install Dependencies: pip install -r requirements.txt <br>
Set up PostgreSQL: Ensure you have PostgreSQL installed and running. The schema and sql dump files are added in '/data' foder. Import these files to set up local db. Update the database connection details in .env file. <br>
Run the Application: streamlit run .\Paperpalooza_Home.py <br>
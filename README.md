# Experimenter_UI  
This is a standlone application to experiment with ETD classifier and summarizer models.  

Entrypoint for the code: Experimenter_Home.py  

To execute Experimenter UI on ARC:  
1. Connect to an ARC instance.  
2. Clone this repository.  
3. Create a virtual environment and install all the packages mentioned in [requirements.txt](requirements.txt).  
4. Create a database and tables as specified in [experimenter_db_dump.sql](experimenter_db_dump.sql).  
5. Specify database file (.db) path in [.env](.env).  
6. Connect to a GPU instance.
7. Run the code using `streamlit run Experimenter_Home.py` command. This will start the streamlit server on the default 8501 port, to change the port, add `server.PORT <port_number>` to the run command.  
8. To access the Experimenter_Home UI, create a two-way SSH tunnel. To do this, run the command in a local terminal: 
`ssh -L 8501:localhost:7862 username@tinkercliffs_host_name ssh -L 7862:localhost:8501 tc-gpu001`  
Here, change the port numbers and the GPU instance as needed.
9. After accessing the UI, open the Classifier page and provide model details on the sidebar: model_name=`allenai/scibert_scivocab_uncased`, model_saved_state=`<Full path to model file. (../experimenter_ui/helpers/Classifier_Util/TitleAbstractScibert_20_64_1e5.pt)>`, model_class=`SciBERT`.
10. Provide ETD chapter text in the text area or by uploading chapter PDF file and classify!  


For any issues, reach out to Kanad Naleshwarkar (kanadn@vt.edu).

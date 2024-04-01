FROM python:3.10-slim

WORKDIR /app

ENV GITLAB_ACCESS_TOKEN default_placeholder

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://kanadn:{GITLAB_ACCESS_TOKEN}@version.cs.vt.edu/kanadn/paperpalooza.git

WORKDIR /app/paperpalooza

RUN pip install -r requirements.txt

# Temporary fix for nltk punkt download
RUN python -c 'import nltk; nltk.download("punkt")' 

EXPOSE 8502

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

ENTRYPOINT ["streamlit", "run", "Paperpalooza_Home.py", "--server.port=8502", "--server.address=0.0.0.0"]
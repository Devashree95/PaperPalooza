FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://kanadn:glpat-N6k13ZWsss9ySa4bM4xZ@version.cs.vt.edu/kanadn/paperpalooza.git

WORKDIR /app/paperpalooza

RUN pip install -r requirements.txt

EXPOSE 8502

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

ENTRYPOINT ["streamlit", "run", "Paperpalooza_Home.py", "--server.port=8502", "--server.address=0.0.0.0"]
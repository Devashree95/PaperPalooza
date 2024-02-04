FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://kanadn:glpat-qvJxcbwh8gj-x2qHw1xk@code.vt.edu/kanadn/experimenter_ui.git

WORKDIR /app/experimenter_ui

RUN pip install -r requirements.txt

EXPOSE 8502

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8502", "--server.address=0.0.0.0"]
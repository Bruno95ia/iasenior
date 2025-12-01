FROM python:3.10-slim

RUN apt-get update && apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY dashboard.py .
COPY resultados ./resultados

RUN pip install --no-cache-dir streamlit pillow numpy

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.address=0.0.0.0", "--server.port=8501"]

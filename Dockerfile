FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim
RUN apt-get update && apt-get install -y supervisor \
                   && rm -rf /var/lib/apt/lists/*
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY . /app
VOLUME ["/mblocks"]
RUN pip install -r requirements.txt --no-cache-dir

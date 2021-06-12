FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

WORKDIR /app/

COPY . /app
ENV PYTHONPATH=/app
VOLUME ["/mblocks/server"]
RUN pip install -r requirements.txt --no-cache-dir

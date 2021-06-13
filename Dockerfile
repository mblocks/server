FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim
COPY . /app
VOLUME ["/mblocks/server"]
RUN pip install -r requirements.txt --no-cache-dir

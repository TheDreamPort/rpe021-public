FROM python:3.10-slim

RUN pip install --no-cache-dir fastapi[all]

COPY rpe021_example.py /opt

WORKDIR /opt
ENTRYPOINT uvicorn rpe021_example:app --host 0.0.0.0 --port 80

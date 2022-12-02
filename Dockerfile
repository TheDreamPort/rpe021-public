FROM ubuntu

WORKDIR /opt

RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip install --no-cache-dir wheel fastapi[all]

COPY rpe021_example.py /opt/rpe021_example.py

ENTRYPOINT uvicorn rpe021_example:app --host 0.0.0.0 --port 80

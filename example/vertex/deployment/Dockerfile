FROM python:3.10-slim-buster

ARG PROJECT_ID
ENV PROJECT_ID=${PROJECT_ID}

COPY vertex_deployer*.tar.gz .
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

COPY vertex .

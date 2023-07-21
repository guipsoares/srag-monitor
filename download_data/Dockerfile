FROM python:3.9
RUN pip3 install --no-cache-dir --upgrade pip

COPY download_data /download_data
WORKDIR /download_data

ARG DRIVE_CREDENTIALS

RUN echo "$DRIVE_CREDENTIALS" > client_secrets.json

RUN pip3 install -r requirements.txt
RUN python3 cache_data.py

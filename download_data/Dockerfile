FROM python:3.9
RUN pip3 install --no-cache-dir --upgrade pip

COPY download_data /download_data
WORKDIR /download_data

ARG DRIVE_CREDENTIALS

RUN echo "$DRIVE_CREDENTIALS" > credentials.json
RUN echo "$CLIENT_SECRETS" > client_secrets.json

RUN pip3 install -r requirements.txt
RUN python3 cache_data.py

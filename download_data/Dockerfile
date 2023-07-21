FROM python:3.9
RUN pip3 install --no-cache-dir --upgrade pip 
RUN apt-get update && apt-get -qq -y install jq

COPY download_data /download_data
WORKDIR /download_data

ARG DRIVE_CREDENTIALS
ARG CLIENT_SECRETS

RUN echo "$DRIVE_CREDENTIALS" | base64 --decode | jq '.' > credentials.json
RUN echo "$CLIENT_SECRETS" | base64 --decode | jq '.' > client_secrets.json

RUN pip3 install -r requirements.txt
RUN python3 cache_data.py

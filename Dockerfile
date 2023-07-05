FROM python:3.9
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir rsconnect-python

COPY . /srag-monitor
WORKDIR /srag-monitor

ARG SHINY_TOKEN
ARG SHINY_SECRET

RUN rsconnect add \
    --account guipsoares \
    --name guipsoares \
    --token $SHINY_TOKEN \
    --secret $SHINY_SECRET
RUN rsconnect deploy shiny . --title srag-monitor
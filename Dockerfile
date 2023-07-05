FROM python:3.9
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir rsconnect-python

COPY . /shinyapp
WORKDIR /shinyapp

ARG SHINY_TOKEN
ARG SHINY_SECRET

RUN echo $SHINY_TOKEN-$SHINY_SECRET
RUN rsconnect add \
    --account guipsoares \
    --name guipsoares \
    --token $SHINY_TOKEN \
    --secret $SHINY_SECRET
RUN rsconnect deploy shiny .
# Use the official lightweight Python image.
# https://hub.docker.com/_/python

FROM python:3.11-slim-bullseye

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Download latest listing of available packages:
RUN apt-get -y update
# Upgrade already installed packages:
RUN apt-get -y upgrade
# Install new packages:
RUN apt-get -y install git libomp-dev build-essential

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -m pip install --no-cache-dir -e .

# Create a temporary directory
RUN mkdir tmp

# Run the web service on container startup.
ENV OMP_NUM_THREADS=8
CMD panel serve app.py --address 0.0.0.0 --port 8080 --allow-websocket-origin="*"
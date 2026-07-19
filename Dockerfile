# Use the official lightweight Python image.
# https://hub.docker.com/_/python
# https://pdm.fming.dev/latest/usage/advanced/#use-pdm-in-a-multi-stage-dockerfile

FROM python:3.12-slim-bookworm

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Download latest listing of available packages:
RUN apt-get -y update
# Upgrade already installed packages:
RUN apt-get -y upgrade
# Install new packages:
RUN apt-get -y install git libpangocairo-1.0-0

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

# Build documentation
RUN cd docs && mkdocs build

# Run the web service on container startup.
# ETC_N_WORKERS sets the ETC engine's ThreadPoolExecutor worker count.
# OMP_NUM_THREADS no longer drives the ETC itself (pfsspecsim v2 is pure
# Python); it is kept to cap the BLAS/OpenMP pools underneath numpy, which
# would otherwise spawn one thread per core inside each ETC worker.
ENV ETC_N_WORKERS=8
ENV OMP_NUM_THREADS=8
CMD panel serve ./app.py --address 0.0.0.0 --port 8080 --allow-websocket-origin="*" --static-dirs doc="./docs/site/"

# TODO
# - Remove temporary files in tmp directory periorically using crontab.
#   https://www.airplane.dev/blog/docker-cron-jobs-how-to-run-cron-inside-containers
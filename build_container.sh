#!/bin/bash

set -euxo pipefail

show_help() {
    echo "Usage: bash ./build_container.sh [-s] [-d] [-g]"
    echo "       -p    Update package dependencies using PDM"
    echo "       -d    Build the Docker image and push it to Docker Hub"
    echo "       -g    Deploy the app to Google Cloud Run"
}

update_pdm_packages() {
    echo "Updating package dependencies to the latest versions"

    # update to the latest packages
    pdm update
    # export package dependencies to requirements.txt
    pdm export -f requirements --without-hashes --prod >requirements.txt
}

docker_image() {
    # build docker image
    echo "Building a Docker image"
    docker image build -t monodera/pfs_etc_web:latest .

    # push docker image
    echo "Pushing the Docker image to Docker Hub"
    docker push monodera/pfs_etc_web:latest
}

gcloud_deploy() {
    # deploy to Google Cloud Run
    echo "Deploy the container to Google Cloud Run"
    gcloud run deploy pfsetcweb --source .
}

while getopts pdg flag; do
    case "${flag}" in
    p) update_pdm_packages ;;
    d) docker_image ;;
    g) gcloud_deploy ;;
    *) show_help ;;
    esac
done

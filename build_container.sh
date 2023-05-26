#!/bin/bash

set -euxo pipefail

show_help() {
    echo "Usage: bash ./build_container.sh [-s] [-d] [-g]"
    echo "       -p    Update package dependencies using PDM"
    echo "       -d    Build the Docker image and push it to Docker Hub"
    echo "       -g    Deploy the app to Google Cloud Run"
}

update_pdm_packages() {
    echo "Update package dependencies to the latest versions"
    # update to the latest packages
    pdm update
    # export package dependencies to requirements.txt
    pdm export -f requirements --without-hashes --prod -G mkdocs >requirements.txt
}

docker_image() {
    # build docker image
    echo "Build a Docker image and push it to Docker Hub"
    docker buildx build --platform=linux/amd64,linux/arm64 -t monodera/pfs_etc_web:latest --push .
    # docker image build -t monodera/pfs_etc_web:latest .
    # push docker image
    # echo "Pushing the Docker image to Docker Hub"
    # docker push monodera/pfs_etc_web:latest
}

gcloud_deploy() {
    # deploy to Google Cloud Run
    echo "Deploy the container to Google Cloud Run"
    gcloud run deploy pfsetcweb --source .

    # delete old revisions
    # gcloud run revisions list --filter="status.conditions.type:Active AND status.conditions.status:'False'" --format='value(metadata.name)' | xargs -r -L1 gcloud run revisions delete --quiet

    # setup cleanup policy (not working, though)
    # gcloud artifacts repositories set-cleanup-policies cloud-run-source-deploy --location=us-west4 --project=friendly-folio-387106 --policy=google_articaft_registry_policy.json --overwrite

}

while getopts pdg flag; do
    case "${flag}" in
    p) update_pdm_packages ;;
    d) docker_image ;;
    g) gcloud_deploy ;;
    *) show_help ;;
    esac
done

#!/bin/bash
set -x

# Necessary environment variables
# PROJECT
# BASE64_MANIFEST
# BUCKET
# BUCKET_PATH


gcloud auth activate-service-account --key-file /tmp/token.json
gcloud config set project ${PROJECT}

echo ${BASE64_MANIFEST} | base64 -d > /tmp/manifest.yml

gsutil cp /tmp/manifest.yml gs://${BUCKET}/${BUCKET_PATH}

echo "SPINNAKER_CONFIG_JSON={\"artifacts\": [{\"type\": \"gcs/object\", \"name\": \"gs://${BUCKET}/${BUCKET_PATH}\", \"reference\": \"gs://${BUCKET}/${BUCKET_PATH}\"}]}"
#!/bin/bash
# Need these env variables:
# SOURCE_ACCOUNT
# SOURCE_REGION
# SOURCE_ROLE_ARN
# SOURCE_IMAGE

# DEST_ACCOUNT
# DEST_REGION
# DEST_ROLE_ARN

mkdir -p /root/.aws

# Generate aws config to get passwords
tee /root/.aws/config <<-EOF
[profile ${SOURCE_ACCOUNT}]
credential_source = Ec2InstanceMetadata
role_arn = ${SOURCE_ROLE_ARN}

[profile ${DEST_ACCOUNT}]
credential_source = Ec2InstanceMetadata
role_arn = ${DEST_ROLE_ARN}
EOF

SOURCE_PASSWORD=$(aws --profile ${SOURCE_ACCOUNT} ecr get-login-password --region ${SOURCE_REGION})
SOURCE_REPO=${SOURCE_ACCOUNT}.dkr.ecr.${SOURCE_REGION}.amazonaws.com
SOURCE_AUTH=$(echo AWS:${SOURCE_PASSWORD} | base64)

DEST_PASSWORD=$(aws --profile ${DEST_ACCOUNT} ecr get-login-password --region ${DEST_REGION})
DEST_REPO=${DEST_ACCOUNT}.dkr.ecr.${DEST_REGION}.amazonaws.com
DEST_AUTH=$(echo AWS:${DEST_PASSWORD} | base64)

# /work/ will be mounted into the Kaniko container at /kaniko/.docker/

# Generate Docker config with credentials
# Will be mounted into kaniko container at /kaniko/.docker/config.json
echo {} | jq "setpath([\"auths\", \"${SOURCE_REPO}\", \"auth\"]; \"${SOURCE_AUTH}\")" \
  | jq "setpath([\"auths\", \"${DEST_REPO}\", \"auth\"]; \"${DEST_AUTH}\")" > /work/config.json


# Dockerfile
tee /work/Dockerfile <<-EOF
FROM ${SOURCE_IMAGE}
EOF
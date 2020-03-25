#!/bin/sh

## Looks for these env variables:
# GIT_USERNAME
# GIT_TOKEN
# GIT_DOMAIN
# GIT_REPO
# GIT_DIRECTORY

# HELM_NAME
# HELM_CHART_NAME
# HELM_SET_NAME
# HELM_SET_VALUE
# HELM_VALUES_FILE
# HELM_NAMESPACE

tee ~/.gitconfig <<-'EOF'
[credential]
  helper = store --file /tmp/.gitcredentials
EOF

tee /tmp/.gitcredentials > /dev/null <<-EOF
https://${GIT_USERNAME}:${GIT_TOKEN}@${GIT_DOMAIN}
EOF

REPO_NAME=$(basename ${GIT_REPO} .git)
git clone ${GIT_REPO}
cd ${REPO_NAME}/${GIT_DIRECTORY}

set -x

helm template ${HELM_NAME} ${HELM_CHART_NAME} --namespace ${HELM_NAMESPACE} --set ${HELM_SET_NAME}="${HELM_SET_VALUE}" --values ${HELM_VALUES_FILE} | tee manifest.yaml
BASE64=$(base64 manifest.yaml | tr -d \\n)
# --values ${HELM_VALUES}

echo "SPINNAKER_CONFIG_JSON={\"artifacts\": [{\"type\":\"embedded/base64\",\"name\": \"chart\", \"reference\": \"${BASE64}\"}]}"
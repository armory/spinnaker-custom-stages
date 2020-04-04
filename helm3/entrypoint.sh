#!/bin/sh

# Sample git repo layout at https://github.com/justinrlee/public-helm-chart
# ./helm
# ./helm/app
# ./helm/app/mychart
# ./helm/app/mychart/test
# ./helm/app/mychart/test/values.yaml
# ./helm/app/mychart/Chart.yaml
# ./helm/app/mychart/charts
# ./helm/app/mychart/.helmignore
# ./helm/app/mychart/templates
# ./helm/app/mychart/templates/deployment.yaml
# ./helm/app/mychart/templates/NOTES.txt
# ./helm/app/mychart/templates/ingress.yaml
# ./helm/app/mychart/templates/tests
# ./helm/app/mychart/templates/tests/test-connection.yaml
# ./helm/app/mychart/templates/service.yaml
# ./helm/app/mychart/templates/serviceaccount.yaml
# ./helm/app/mychart/templates/_helpers.tpl
# ./helm/app/mychart/values.yaml

## Looks for these env variables:
# GIT_USERNAME : username used for git clone
# GIT_TOKEN : token used for git clone (e.g., Github PAT)
# GIT_DOMAIN : domain name for Github / GHE instance (e.g., github.com, or github.orgname.com)
# GIT_REPO : git URL for helm chart repo. Used for git clone.  (e.g., https://github.com/justinrlee/public-helm-chart.git)
# GIT_DIRECTORY : Path within git repository where helm chart directory lives.  In the above example, the chart is at /helm/app/mychart, so GIT_DIRECTORY would be `helm/chart`

# HELM_NAME : (Optional) Helm release name
# HELM_CHART_NAME : Name for the directory where the helm chart is.  In the above example, this would be `mychart`
# HELM_SET_NAME : MVP ccurrently only supports one --set field.  This is the "value" for the set
# HELM_SET_VALUE : MVP currently only supports one --set field.  This is the "value" for the set
# HELM_VALUES_FILE : MVP currently supports one "Value file".  This is the relative path to the values file, from the GIT_DIRECTORY.  In the above example, this is mychart/test/values.yaml
# HELM_NAMESPACE : Kubernetes Namespace to do the helm template in

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
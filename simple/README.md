# Simple Custom Stage Definition
This custom stage which runs as a Kubernetes job will fetch pre-configured data from https://webhook.site. The pipeline definition shows how to access that data via SpEL.

## Setup

### Destination Kubernetes cluster
On the Kubernetes cluster where this custom job will run do the following:
* Create a namespace called `runjob`
* (Optional) Enable the TTL Controller for Finished Resources. See https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/

### Spinnaker
* In the Spinnaker UI create an application called `testrj` if it doesn't already exist.
* If this namespace is not managed by Clouddriver then also add an account definition for this namespace to Clouddriver

### Set up JSON payload at webhook.site
* Go to https://webhook.site and Click on the Edit button in the top right
* Add the following to the Response Body section
  ```
  SPINNAKER_CONFIG_JSON={"GARDEN_NAME":"botanical","GARDEN_THINGS":{"flowers":[{"name":"lavender","type":"perennial"}],"insects":[{"name":"morpho","type":"butterfly"}]}}
  ```
* Click Copy URL
* Test the URL by running `curl -s $YOUR_WEBHOOK_SITE_URL`

### Edit the files
Edit the YML files in this directory and the file rj-pipeline-def.json. Replace the webhook.site URL with `$YOUR_WEBHOOK_SITE_URL`

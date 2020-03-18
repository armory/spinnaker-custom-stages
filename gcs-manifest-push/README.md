# GCS Push Manifest

This container allows you push a Kubernetes manifest (or any base64 object, really) up to GCS.

It should create an artifact of type `gcs/object` if you capture "Log" output from the container "push"

## Create Secret

```bash
# Create the secret
kubectl -n spinnaker create secret generic gcs-token --from-file gcs.json
```

## Sample manifest to run directly

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: push-manifest-to-gcs
  namespace: spinnaker
spec:
  backoffLimit: 0
  template:
    spec:
      containers:
        - 
          name: push
          env:
            - name: BASE64_MANIFEST
              value: '${base64_manifest}'
            - name: PROJECT
              value: cloud-armory
            - name: BUCKET
              value: justin-cloud-armory
            - name: BUCKET_PATH
              value: manifest.yml
          image: 'justinrlee/push-gcs:2020-03-18'
          volumeMounts:
            - mountPath: /tmp/token.json
              name: gcs-token
              subPath: gcs.json
      restartPolicy: Never
      volumes:
        - name: gcs-token
          secret:
            secretName: gcs-token
  ttlSecondsAfterFinished: 600

```

## Sample usage to create a Spinnaker stage

```yml
# This goes in /home/spinnaker/.hal/default/profiles/orca-local.yml
# (Create this file if it does not exist)
job:
  preconfigured:
    kubernetes:
      - label: Push Manifest to GCS
        type: gcsPush
        # this defines the 'type' of the stage in the stage definition
        description: Push Kubernetes manifest to GCS
        cloudProvider: kubernetes
        account: spinnaker
        # ^ cloud provider account for both account and credentials
        credentials: spinnaker
        # ^ cloud provider account for both account and credentials
        waitForCompletion: true
        application: spin
        # ^ must exist, must have at least one server group
        propertyFile: jira
        # ^ which container to look in for SPINNAKER_CONFIG_JSON
        parameters:
          - name: manifest
            label: Kubernetes Manifest
            description: Kubernetes Manifest
            mapping: manifest.spec.template.spec.containers[0].env[0].value
            defaultValue: "${base64_manifest}"
          - name: bucket
            label: Bucket
            description: Bucket to push manifest to
            mapping: manifest.spec.template.spec.containers[0].env[1].value
            defaultValue: "bucketname"
          - name: key
            label: Bucket Path
            description: Path in bucket to store manifest
            mapping: manifest.spec.template.spec.containers[0].env[2].value
            defaultValue: "path/to/manifest.yml"
        manifest:
          apiVersion: batch/v1
          kind: Job
          metadata:
            name: push-manifest-to-gcs
            namespace: spinnaker
          spec:
            backoffLimit: 0
            template:
              spec:
                containers:
                  - 
                    name: push
                    env:
                      - name: BASE64_MANIFEST
                        value: 'WILL_BE_REPLACED'
                      - name: BUCKET
                        value: justin-cloud-armory
                      - name: BUCKET_PATH
                        value: manifest.yml
                      - name: PROJECT
                        value: cloud-armory
                    image: 'justinrlee/push-gcs:2020-03-18'
                    volumeMounts:
                      - mountPath: /tmp/token.json
                        name: gcs-token
                        subPath: gcs.json
                restartPolicy: Never
                volumes:
                  - name: gcs-token
                    secret:
                      secretName: gcs-token
            ttlSecondsAfterFinished: 600
```

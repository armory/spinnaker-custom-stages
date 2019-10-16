# Datadog Monitor

This container allows you to monitor a specific Datadog monitor for health for some duration (period * interval)

## Create Secret

```bash
kubectl -n test create secret datadog-keys --from-literal=dd_api_key=x --from-literal=dd_app_key=y
```

## Sample manifest

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: datadog-test
  namespace: test
spec:
  backoffLimit: 0
  template:
    spec:
      containers:
        - name: datadog
          env:
            - name: DD_API_KEY
              valueFrom:
                secretKeyRef:
                  name: datadog-keys
                  key: dd_api_key
            - name: DD_APP_KEY
              valueFrom:
                secretKeyRef:
                  name: datadog-keys
                  key: dd_app_key
            - name: DD_MONITOR_ID
              value: '9631699'
            - name: COUNT
              value: '10'
            - name: INTERVAL
              value: '30'
          image: 'justinrlee/rj-datadog-monitor:1571103399'
      restartPolicy: Never
  ttlSecondsAfterFinished: 600
```

## Sample usage to create a Spinnaker stage

```yml
# This goes in /home/spinnaker/.hal/default/profiles/orca-local.yml
# (Create this file if it does not exist)
job:
  preconfigured:
    kubernetes:
      - label: Check Datadog Monitor
        type: checkDatadog
        # this defines the 'type' of the stage in the stage definition
        description: Check Datadog monitor
        cloudProvider: kubernetes
        account: spinnaker
        # ^ cloud provider account for both account and credentials
        credentials: spinnaker
        # ^ cloud provider account for both account and credentials
        waitForCompletion: true
        application: spin
        # ^ must exist, must have at least one server group
        propertyFile: datadog-monitor
        # ^ which container to look in for SPINNAKER_CONFIG_JSON
        parameters:
          - name: Monitor
            label: Monitor ID
            description: Datadog monitor ID to monitor
            mapping: manifest.spec.template.spec.containers[0].env[2].value
            defaultValue: "9631699"
          - name: Count
            label: Count
            description: Number of polls to run
            mapping: manifest.spec.template.spec.containers[0].env[3].value
            defaultValue: "4"
          - name: Interval
            label: Interval
            description: Interval between polls
            mapping: manifest.spec.template.spec.containers[0].env[4].value
            defaultValue: "15"
        manifest:
          apiVersion: batch/v1
          kind: Job
          metadata:
            name: datadog-monitor
            namespace: spinnaker
          spec:
            backoffLimit: 0
            template:
              spec:
                containers:
                  - env:
                      - name: DD_API_KEY
                        valueFrom:
                          secretKeyRef:
                            key: dd_api_key
                            name: datadog-keys
                      - name: DD_APP_KEY
                        valueFrom:
                          secretKeyRef:
                            key: dd_app_key
                            name: datadog-keys
                      - name: DD_MONITOR_ID
                        value: '9631699'
                      - name: COUNT
                        value: '4'
                      - name: INTERVAL
                        value: '15'
                    image: 'justinrlee/rj-datadog-monitor:1571139655'
                    name: datadog
                restartPolicy: Never
            ttlSecondsAfterFinished: 60
```

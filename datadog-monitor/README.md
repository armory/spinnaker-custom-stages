# Does stuff

Create Secret

```bash
kubectl -n test create secret datadog-keys --from-literal=dd_api_key=x --from-literal=dd_app_key=y
```

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

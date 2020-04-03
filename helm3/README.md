#

Create a secret for this:

```
kubectl -n spinnaker create secret generic git-creds --from-literal=username=justinrlee --from-literal=token=abcd
```

More generic one:
```
[3/27 11:21 AM] Justin (Guest)
    
apiVersion: batch/v1
kind: Job
metadata:
  name: helm3-generator
  namespace: spinnaker
spec:
  backoffLimit: 0
  template:
    spec:
      containers:
        - env:
            - name: GIT_USERNAME
              valueFrom:
                secretKeyRef:
                  key: username
                  name: git-creds
            - name: GIT_TOKEN
              valueFrom:
                secretKeyRef:
                  key: token
                  name: git-creds
            - name: GIT_DOMAIN
              value: github.com
            - name: GIT_REPO
              value: 'https://github.com/justinrlee/private-helm-chart'
            - name: GIT_DIRECTORY
              value: helm/app
            - name: HELM_RELEASE
              value: mychart123
            - name: HELM_CHART_NAME
              value: mychart
            - name: HELM_NAMESPACE
              value: spinnaker
            - name: HELM_CUSTOM_PARAMS
              value: '--set x=y --values mychart/test/values.yaml'
          image: 'justinrlee/helm3:custom'
          imagePullPolicy: Always
          name: helm3-generator
      restartPolicy: Never
```

Run Job:
```
apiVersion: batch/v1
kind: Job
metadata:
  name: helm3-generator
  namespace: spinnaker
spec:
  template:
    spec:
      containers:
        - env:
            - name: GIT_USERNAME
              valueFrom:
                secretKeyRef:
                  key: username
                  name: git-creds
            - name: GIT_TOKEN
              valueFrom:
                secretKeyRef:
                  key: token
                  name: git-creds
            - name: GIT_DOMAIN
              value: github.com
            - name: GIT_REPO
              value: 'https://github.com/justinrlee/private-helm-chart'
            - name: GIT_DIRECTORY
              value: helm/app
            - name: HELM_NAME
              value: mychart
            - name: HELM_CHART_NAME
              value: mychart
            - name: HELM_SET_NAME
              value: x
            - name: HELM_SET_VALUE
              value: 'y'
            - name: HELM_VALUES_FILE
              value: mychart/test/values.yaml
            - name: HELM_NAMESPACE
              value: spinnaker
          image: 'justinrlee/helm3:latest'
          imagePullPolicy: Always
          name: helm3-generator
      restartPolicy: Never
```
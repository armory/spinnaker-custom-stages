# GitLab Stage

This container allows you to trigger a GitLab pipeline (which lives in a repo, and is attached to a specific branch), wait for it to complete, and gather information about the triggered pipeline.

## Create Secret

```bash
kubectl -n test create secret generic gitlab --from-literal=GITLAB_TOKEN=<PERSONAL_ACCESS_TOKEN>
```

## Sample manifest to run directly

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: gitlab-test
  namespace: root-change
spec:
  backoffLimit: 0
  template:
    spec:
      containers:
        - name: datadog
          env:
            - name: GITLAB_TOKEN
              valueFrom:
                secretKeyRef:
                  name: gitlab
                  key: GITLAB_TOKEN
            - name: GITLAB_URL
              value: 'http://gitlab.domain.com
            - name: PROJECT_NAME
              value: 'superteam/my-awesome-project'
            - name: BRANCH
              value: 'master'
          image: 'justinrlee/rj-gitlab:1571415673'
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
      - label: GitLab
        type: gitlab
        # this defines the 'type' of the stage in the stage definition
        description: Run GitLab Pipeline
        cloudProvider: kubernetes
        account: spinnaker
        # ^ cloud provider account for both account and credentials
        credentials: spinnaker
        # ^ cloud provider account for both account and credentials
        waitForCompletion: true
        application: spin
        # ^ must exist, must have at least one server group
        propertyFile: gitlab
        # ^ which container to look in for SPINNAKER_CONFIG_JSON
        parameters:
          - name: Project Name
            label: Project Name
            description: Fully qualified Project Name (e.g., 'superteam/my-awesome-project')
            mapping: manifest.spec.template.spec.containers[0].env[2].value
            defaultValue: "superteam/my-awesome-project"
          - name: Branch
            label: Branch
            description: Branch to run on
            mapping: manifest.spec.template.spec.containers[0].env[3].value
            defaultValue: "master"
          - name: Interval
            label: Interval
            description: Interval between polls
            mapping: manifest.spec.template.spec.containers[0].env[4].value
            defaultValue: "60"
          - name: Duration
            label: Duration
            description: Maxinum number of polls before failing (0 for no limit)
            mapping: manifest.spec.template.spec.containers[0].env[5].value
            defaultValue: "60"
          - name: Job Name
            label: Job Name
            description: Name of job to pull artifact from (empty for no artifact)
            mapping: manifest.spec.template.spec.containers[0].env[6].value
            defaultValue: ""
          - name: Artifact Name
            label: Artifact Name
            description: File name of artifact to read metadata from (empty for no artifact)
            mapping: manifest.spec.template.spec.containers[0].env[7].value
            defaultValue: ""
        manifest:
          apiVersion: batch/v1
          kind: Job
          metadata:
            name: gitlab-test
            namespace: root-change
          spec:
            backoffLimit: 0
            template:
              spec:
                containers:
                  - name: gitlab
                    env:
                      - name: GITLAB_TOKEN
                        valueFrom:
                          secretKeyRef:
                            name: gitlab
                            key: GITLAB_TOKEN
                      - name: GITLAB_URL
                        value: 'http://gitlab.domain.com'
                      - name: PROJECT_NAME
                        value: 'superteam/my-awesome-project'
                      - name: BRANCH
                        value: 'master'
                      - name: INTERVAL
                        value: '60'
                      - name: MAX_WAIT
                        value: '60'
                      - name: JOB_NAME
                        value: 'rspec'
                      - name: ARTIFACT_NAME
                        value: 'build.properties'
                    image: 'justinrlee/rj-gitlab:1571415673'
                restartPolicy: Never
            ttlSecondsAfterFinished: 600
```

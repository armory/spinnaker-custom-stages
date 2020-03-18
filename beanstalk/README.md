# Beanstalk create app version

This container allows you to create a beanstalk app version from an s3 bucket bundle, using an assumed role

## Sample manifest

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: beanstalk-create-app-version-from-s3
  namespace: spinnaker
spec:
  backoffLimit: 0
  template:
    spec:
      containers:
        - name: beanstalk
          env:
            - name: ASSUME_ROLE_ARN
              value: 'arn:aws:iam::111122223333:role/assumeableRole'
            - name: APPLICATION_NAME
              value: 'my-beanstalk-app'
            - name: VERSION_LABEL
              value: 'version-123'
            - name: REGION
              value: 'us-west-2'
            - name: S3_BUCKET
              value: 'my-s3-bucket'
            - name: S3_KEY
              value: 'file.zip'
            - name: VERSION_DESCRIPTION
              value: 'This is version 123'
          image: 'justinrlee/beanstalk-create-app-version-from-s3:latest'
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
      - label: "Beanstalk: Create Application Version from S3"
        type: beanstalkCreateAppVersion
        # this defines the 'type' of the stage in the stage definition
        description: Create a Beanstalk Application Version from an S3 Bundle
        cloudProvider: kubernetes
        account: spinnaker
        # ^ cloud provider account for both account and credentials
        credentials: spinnaker
        # ^ cloud provider account for both account and credentials
        waitForCompletion: true
        application: spin
        # ^ must exist, must have at least one server group
        propertyFile: beanstalk
        # ^ which container to look in for SPINNAKER_CONFIG_JSON
        parameters:
          - name: Role ARN
            label: Role ARN
            description: Role ARN to assume
            mapping: manifest.spec.template.spec.containers[0].env[0].value
            defaultValue: "arn:aws:iam::111122223333:role/assumeableRole"
          - name: Application Name
            label: Application Name
            description: Name of the Beanstalk Application
            mapping: manifest.spec.template.spec.containers[0].env[1].value
            defaultValue: "my-beanstalk-app"
          - name: Version Label
            label: Version Label
            description: Version Label for the new EBS Application Version
            mapping: manifest.spec.template.spec.containers[0].env[2].value
            defaultValue: "version-123"
          - name: Region
            label: Region
            description: AWS Region where app and S3 bucket are
            mapping: manifest.spec.template.spec.containers[0].env[3].value
            defaultValue: "us-west-2"
          - name: S3 Bucket
            label: S3 Bucket
            description: S3 Bucket where the bundle exists (must be in same region as the EBS App)
            mapping: manifest.spec.template.spec.containers[0].env[4].value
            defaultValue: "my-s3-bucket"
          - name: S3 Bucket Key
            label: S3 Bucket Key
            description: Path in the S3 bucket where the bundle is
            mapping: manifest.spec.template.spec.containers[0].env[5].value
            defaultValue: "file.zip"
          - name: Version Description
            label: Version Description
            description: Version Description
            mapping: manifest.spec.template.spec.containers[0].env[6].value
            defaultValue: "This is a generic description"
        manifest:
          apiVersion: batch/v1
          kind: Job
          metadata:
            name: beanstalk-create-app-version-from-s3
            namespace: spinnaker
          spec:
            backoffLimit: 0
            template:
              spec:
                containers:
                  - name: beanstalk
                    env:
                      - name: ASSUME_ROLE_ARN
                        value: 'arn:aws:iam::111122223333:role/assumeableRole'
                      - name: APPLICATION_NAME
                        value: 'my-beanstalk-app'
                      - name: VERSION_LABEL
                        value: 'version-123'
                      - name: REGION
                        value: 'us-west-2'
                      - name: S3_BUCKET
                        value: 'my-s3-bucket'
                      - name: S3_KEY
                        value: 'file.zip'
                      - name: VERSION_DESCRIPTION
                        value: 'This is version 123'
                    image: 'justinrlee/beanstalk-create-app-version-from-s3:latest'
                restartPolicy: Never
            ttlSecondsAfterFinished: 600
```

# ECR Promote

This pod allows you to pull a Docker image from one ECR repository and push it to another, using assumed roles.

The pod must be able to assume a role in both the source and destination AWS accounts (that has the permissions to pull and push Docker images)

Here's how it works:
* There is an initContainer with `aws-cli` and `jq`, which does the following:
  * Has a shared emptyDir mounted at `/work`
  * Creates a .aws/config file with profiles with the two assumed role ARNs
  * Assumes the role in each of the target AWS accounts, and uses `aws ecr get-login-password` to get an (ephemeral) Docker password
  * Uses jq to generate a Docker `config.json` file 
    * Created at `/work/config.json` in the initContainer
    * Will be mounted in the second container at `/work/.docker/config.json`)
  * Also generates a single-line Dockerfile of `FROM <SOURCE_IMAGE>`
    * Created at `/work/Dockerfile` in the initContainer
    * Will be mounted in primary container at `/work/.docker/Dockerfile`)
* Once the initContainer finishes generating the Docker config.json and Dockerfile, it stops, and the primary container runs:
  * We give Kaniko the Docker config.json (which has credentials for both AWS accounts)
  * We also give Kaniko the Dockerfile (which is essentially just "download the source image")
  * We give Kaniko a destination Docker repository, where it pushes the image once it's done downloading the source image

This is the manifest:

```yml
apiVersion: batch/v1
kind: Job
metadata:
  name: ecr-promote-test
  # namespace: spinnaker
spec:
  backoffLimit: 0
  template:
    spec:
      volumes:
        - name: workdir
          emptyDir: {}
      initContainers:
        - name: ecr-init
          image: justinrlee/ecr:mvp
          env:
          - name: SOURCE_ACCOUNT
            value: "123456789012"
            # ^ This is the AWS account ID where the image is being pulled from
          - name: DEST_ACCOUNT
            value: "111222333444"
            # ^ This is the AWS account ID where the image is being pushed to
          - name: SOURCE_REGION
            value: "us-west-2"
            # ^ AWS region where image is being pulled from
          - name: DEST_REGION
            value: "us-west-2"
            # ^ AWS region where image is being pushed to
          - name: SOURCE_ROLE_ARN
            value: "arn:aws:iam::123456789012:role/ecr-role"
            # ^ ARN for AWS IAM Role that will be assumed to pull the source image (must be assumable by the pod)
          - name: DEST_ROLE_ARN
            value: "arn:aws:iam::111222333444:role/ecr-role"
            # ^ ARN for AWS IAM Role that will be assumed to push the destination image (must be assumable by the pod)
          - name: SOURCE_IMAGE
            value: "123456789012.dkr.ecr.us-west-2.amazonaws.com/my-image/my-repo:my-tag"
            # ^ Fully qualified docker image name for source image
          volumeMounts:
          - name: workdir
            mountPath: /work
      containers:
        - name: kaniko-push-pull
          image: 'gcr.io/kaniko-project/executor:latest'
          args:
          - "--dockerfile"
          - "/kaniko/.docker/Dockerfile"
          - "--verbosity"
          - "debug"
          - "--destination"
          - "111222333444.dkr.ecr.us-west-2.amazonaws.com/my-image/my-repo:my-tag"
          # ^ Fully qualified docker image name for destination image
          volumeMounts:
          - name: workdir
            mountPath: /kaniko/.docker
      restartPolicy: Never
  ttlSecondsAfterFinished: 600
```


## Sample usage to create a Spinnaker stage

See other run job examples for how to parameterize the above.
import argparse
import os
import json

import boto3
import sys

class EnvDefault(argparse.Action):
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required, 
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python script that creates an Elastic Beanstalk Application Version from an S3 bundle, using assume role.  We assume a single role for all actions')

    parser.add_argument(
        "-L", "--version-label", action=EnvDefault, envvar="VERSION_LABEL",
        help="Specify the Version Label for the new Application Version (can also be specified with env variable VERSION_LABEL)"
    )

    parser.add_argument(
        "-a", "--application-name", action=EnvDefault, envvar="APPLICATION_NAME",
        help="Specify the Beanstalk Applicion for the new Application Version to be created in (can also be specified with env variable APPLICATION_NAME)"
    )

    parser.add_argument(
        "-r", "--assume-role-arn", action=EnvDefault, envvar="ASSUME_ROLE_ARN",
        help="Specify the IAM Role to Assume (can also be specified with env variable ASSUME_ROLE_ARN)"
    )

    parser.add_argument(
        "-R", "--region", action=EnvDefault, envvar="REGION",
        help="Specify the AWS Region (both the EBS Application and Bucket must be in this region) (can also be specified with env variable REGION)"
    )

    parser.add_argument(
        "-D", "--version-description", action=EnvDefault, envvar="VERSION_DESCRIPTION",
        help="Specify the version description (can also be specified with env variable VERSION_DESCRIPTION)"
    )

    parser.add_argument(
        "-B", "--s3-bucket", action=EnvDefault, envvar="S3_BUCKET",
        help="Specify the S3 Bucket where the source bundle exists (can also be specified with env variable S3_BUCKET)"
    )

    parser.add_argument(
        "-K", "--s3-key", action=EnvDefault, envvar="S3_KEY",
        help="Specify the S3 Bucket Key where the source bundle exists (can also be specified with env variable S3_KEY)"
    )    

    args = parser.parse_args()

    RoleArn = args.assume_role_arn
    VersionLabel = args.version_label
    ApplicationName = args.application_name
    Description = args.version_description
    Region = args.region
    S3Bucket = args.s3_bucket
    S3Key = args.s3_key

    RoleSessionName = "BeanstalkCreateAppVersion"

    try:
        # https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-api.html
        sts_client = boto3.client('sts')
        assumed_role_object = sts_client.assume_role(
            RoleArn=RoleArn,
            RoleSessionName=RoleSessionName
        )

        credentials = assumed_role_object['Credentials']

    except Exception as e:
        print(F"Unable to assume role {RoleArn}")
        print(e)
        sys.exit(1)

    try:
        remote_beanstalk_client = boto3.client('elasticbeanstalk',
            region_name=Region,
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )

        response = remote_beanstalk_client.create_application_version(
            ApplicationName=ApplicationName,
            VersionLabel=VersionLabel,
            Description=Description,
            SourceBundle={
                'S3Bucket': S3Bucket,
                'S3Key': S3Key
            },
            AutoCreateApplication = True,
            Process = True
        )

        print(F"Creating Elastic Beanstalk application version {VersionLabel} for EBS app {ApplicationName}")
        print(F"Using description '{Description}', and source bundle s3://{S3Bucket}/{S3Key}")

        # print(json.dumps(response['ResponseMetadata']))
        # This is a little bit of a hack
        response['ApplicationVersion']['DateCreated'] = str(response['ApplicationVersion']['DateCreated'])
        response['ApplicationVersion']['DateUpdated'] = str(response['ApplicationVersion']['DateUpdated'])
        
        print(F"SPINNAKER_CONFIG_JSON={json.dumps(response)}")

    except Exception as e:
        print("Unable to create application version:")
        print(e)
        sys.exit(1)


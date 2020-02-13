FROM python:3.7-alpine

RUN pip3 install boto3

ADD create_app_version_from_s3.py /

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/usr/local/bin/python3", "/create_app_version_from_s3.py"]
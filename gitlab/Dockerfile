FROM python:3.7-alpine

RUN pip3 install requests

ADD job.py /

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/usr/local/bin/python3", "/job.py"]
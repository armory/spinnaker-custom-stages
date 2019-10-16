FROM python:3.7-alpine

RUN pip3 install requests

# RUN mkdir -p /var/www/

ADD app.py /

ENV PYTHONUNBUFFERED=1

# EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/python3", "/app.py"]
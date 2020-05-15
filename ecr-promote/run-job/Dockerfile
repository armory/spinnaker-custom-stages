FROM amazon/aws-cli:2.0.14

RUN curl -L https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 \
  -o /usr/local/bin/jq \
  && chmod +x /usr/local/bin/jq

ADD entrypoint.sh /entrypoint.sh

ENTRYPOINT /entrypoint.sh
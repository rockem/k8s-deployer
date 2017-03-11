FROM openjdk:8-jdk-alpine

ENV DISTRIBUTION=build/distributions \
    APP_HOME=/opt/service

RUN apk --no-cache add bash

# ADD automatically extracts tar files
ADD $DISTRIBUTION/*.tar /opt

WORKDIR ${APP_HOME}

EXPOSE 8080

CMD bin/service
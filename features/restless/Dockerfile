FROM python:2.7-slim

ARG VERSION=1
ENV APP_VERSION=${VERSION}

RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

#copy code
COPY . /opt/restless

#define temp workdir
WORKDIR /opt/restless/

ENTRYPOINT ["python"]

CMD ["restless.py"]
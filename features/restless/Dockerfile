FROM alpine:3.3

ARG VERSION=1
ENV APP_VERSION=${VERSION}

RUN apk --no-cache add py-pip wget \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -U pip

#copy code
COPY . /opt/restless

#define temp workdir
WORKDIR /opt/restless/

ENTRYPOINT ["python"]

CMD ["restless.py"]
FROM alpine:3.3

ARG VERSION=1
ENV APP_VERSION=${VERSION}

RUN apk --no-cache add py-pip wget \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -U pip
    && pip install -U pip

#copy code
COPY . /opt/hello

#define temp workdir
WORKDIR /opt/hello/

#dependecies installations
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["hello.py"]
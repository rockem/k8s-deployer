FROM alpine:3.3

ARG VERSION
ENV APP_VERSION=${VERSION}

RUN apk --no-cache add py-pip wget \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -U pip

#copy code
COPY . /opt/app

#define temp workdir
WORKDIR /opt/app/

#dependecies installations
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["app.py"]
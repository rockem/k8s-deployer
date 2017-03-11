FROM alpine:3.3

RUN apk --no-cache add py-pip wget \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -U pip

#copy code
COPY . /opt/sick

#define temp workdir
WORKDIR /opt/sick/

#dependecies installations
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["sick.py"]
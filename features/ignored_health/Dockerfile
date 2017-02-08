FROM python:2.7-slim

RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

#copy code
COPY . /opt/app

#define temp workdir
WORKDIR /opt/app/

RUN touch /opt/app/ignore_blue_green

#dependecies installations
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["app.py"]
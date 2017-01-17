FROM python:2.7-slim

RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

#copy code
COPY . /opt/sick

#define temp workdir
WORKDIR /opt/sick/

#dependecies installations
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["sick.py"]
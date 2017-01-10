FROM python:2.7

#copy code
COPY . /opt/healthy

#define temp workdir
WORKDIR /opt/healthy/

#dependecies installations
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["healthy.py"]
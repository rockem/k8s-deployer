FROM python:2.7

#copy code
COPY . /opt/sick

#define temp workdir
WORKDIR /opt/sick/

#dependecies installations
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["sick.py"]
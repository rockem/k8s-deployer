FROM docker


#RUN apt-get --assume-yes install software-properties-common
#
##python installation
#RUN add-apt-repository ppa:fkrull/deadsnakes-python2.7
#RUN apt-get update
#RUN apt-get --assume-yes install python2.7

RUN apk add --no-cache python && \
    python -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip install --upgrade pip setuptools && \
    rm -r /root/.cache

#pip installation
#RUN apt-get --assume-yes install python-pip
#
#aws profile installation
RUN pip install awscli --ignore-installed six
RUN aws configure set aws_access_key_id AKIAJTCRJYJZ3MKMILYQ
RUN aws configure set aws_secret_access_key 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

#copy code
COPY . /opt/app
#dependecies installations
RUN pip install -r /opt/app/requirements.txt

RUN chmod +x /opt/app/*

WORKDIR /opt/app

CMD $(aws ecr get-login --region us-east-1) && python deployer/deployer.py ${IMAGE_NAME}
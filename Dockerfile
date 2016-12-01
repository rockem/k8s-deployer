FROM docker


# install kubectl
ENV KUBECTL_VERSION 1.2.0

RUN apk add curl ca-certificates && \
    curl -s -L https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl -o /usr/bin/kubectl && \
    chmod +x /usr/bin/kubectl && \
    kubectl version -c

# install python
RUN apk add --no-cache python && \
    python -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip install --upgrade pip setuptools && \
    rm -r /root/.cache

# install aws cli profile
RUN pip install awscli --ignore-installed six
RUN aws configure set aws_access_key_id AKIAJTCRJYJZ3MKMILYQ
RUN aws configure set aws_secret_access_key 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

#copy code
COPY . /opt/app

#dependecies installations
RUN pip install -r /opt/app/requirements.txt

#change permissions files
RUN chmod +x /opt/app/*

WORKDIR /opt/app

# login to aws and run script
CMD $(aws ecr get-login --region us-east-1) && python deployer/deployer.py ${IMAGE_NAME}
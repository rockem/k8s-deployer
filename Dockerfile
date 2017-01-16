FROM docker:1.11.2

# install kubectl
ENV KUBECTL_VERSION 1.2.0

RUN apk add curl ca-certificates && \
    curl -s -L https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl -o /usr/bin/kubectl && \
    chmod +x /usr/bin/kubectl && \
    kubectl version --client

# install python
RUN apk add --no-cache python && \
    python -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip install --upgrade pip setuptools && \
    rm -r /root/.cache

# install git
RUN apk add --no-cache git=2.8.3-r0

# install aws cli profile
RUN pip install awscli --ignore-installed six

#copy code
COPY . /opt/deployer

#dependecies installations
RUN pip install -r /opt/deployer/requirements.txt
RUN pip install --trusted-host om-artifactory.mm.local -i http://om-artifactory.mm.local:8081/artifactory/api/pypi/pypi-platform/simple KubectlConf

#define temp workdir
WORKDIR /opt/deployer

#run service unit tests
RUN python -m nose test

#define workspace
WORKDIR /kubebase

# login to aws and run script
ENTRYPOINT [aws configure set aws_access_key_id ${KEY_ID},
    aws configure set aws_secret_access_key ${ACCESS_KEY}
    "/opt/deployer/deployer_complete.sh"]
]

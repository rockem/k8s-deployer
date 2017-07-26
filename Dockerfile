FROM docker:1.11.2

# install kubectl
ENV KUBECTL_VERSION 1.5.1
ENV KOPS_VERSION 1.5.1

RUN apk add curl ca-certificates && \
    curl -s -L https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl -o /usr/bin/kubectl && \
    chmod +x /usr/bin/kubectl && \
    kubectl version --client

#install kops
RUN  curl -s -L https://github.com/kubernetes/kops/releases/download/${KOPS_VERSION}/kops-linux-amd64 -o /usr/bin/kops \
     && chmod +x /usr/bin/kops


# install python
RUN apk add --no-cache python && \
    python -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip install --upgrade pip setuptools && \
    rm -r /root/.cache

# install git
RUN apk add --no-cache git=2.8.5-r0

# install aws cli profile
RUN pip install awscli --ignore-installed six

#copy code
COPY . /opt/deployer

#dependecies installations
RUN pip install -r /opt/deployer/requirements.txt
RUN pip install --trusted-host 172.31.194.4 -i http://172.31.194.4:8081/artifactory/api/pypi/pypi-platform/simple KubectlConf

#define temp workdir
WORKDIR /opt/deployer

#run service unit tests
RUN python -m nose test

#define workspace
WORKDIR /kubebase

# login to aws and run script
ENTRYPOINT ["/opt/deployer/deployer_complete.sh"]


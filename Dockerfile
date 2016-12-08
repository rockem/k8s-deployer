FROM docker:1.11.2

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
RUN aws configure set aws_access_key_id AKIAJUHGHBF4SEHXKLZA
 RUN aws configure set aws_secret_access_key pzHyzfkDiOLeFJVhwXjSxm4w0UNHjRQCGvencPzx

#copy code
COPY . /opt/deployer

#dependecies installations
RUN pip install -r /opt/deployer/requirements.txt

#define temp workdir
WORKDIR /opt/deployer

#run service unit tests
RUN python -m nose test

#define workspace
WORKDIR /kubebase

#create dirs for sync with k8s env @ amazon
RUN mkdir .cfssl
RUN mkdir ~/.kube

# login to aws and run script
CMD  docker version && $(aws ecr get-login --region us-east-1) && \
           cd /opt/deployer && \
           python kubectlconf/app.py "config-prod" && \
            python deployer/deployer.py ${IMAGE_NAME}
FROM 911479539546.dkr.ecr.us-east-1.amazonaws.com/aws-k8s-docker

#copy code
COPY . /opt/deployer

#dependecies installations
RUN pip install -r /opt/deployer/requirements.txt

#define temp workdir
WORKDIR /opt/deployer


#run service unit tests
RUN python -m nose test

# login to aws and run script
ENTRYPOINT ./deployer_complete.sh
CMD []


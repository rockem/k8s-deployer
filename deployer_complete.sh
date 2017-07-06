#!/bin/sh

aws configure set aws_access_key_id $KEY_ID
aws configure set aws_secret_access_key $ACCESS_KEY

kubectl-conf ${TARGET_ENV}

docker version
$(aws ecr get-login --region us-east-1)
cd /opt/deployer && python deployer/deployer.py "$@"
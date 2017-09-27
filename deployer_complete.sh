#!/bin/sh

aws configure set aws_access_key_id $KEY_ID
aws configure set aws_secret_access_key $ACCESS_KEY

prefix="${TARGET_ENV%%:*}"
export DOMAIN = $DOMAIN

if [ "$prefix" == "kops" ]
then
  export TARGET_ENV="${TARGET_ENV#*:}"
  options="--kops"
else
  options=""
fi

kubectl-conf $TARGET_ENV $options
$(aws ecr get-login --region us-east-1)
cd /opt/deployer && python deployer/app.py "$@"
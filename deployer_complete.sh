#!/bin/sh

aws configure set region us-east-1
aws configure set aws_access_key_id $ACCESS_KEY_ID
aws configure set aws_secret_access_key $SECRET_KEY


prefix="${TARGET_ENV%%:*}"

if [ "$prefix" == "kops" ]
then
  export TARGET_ENV="${TARGET_ENV#*:}"
  options="--kops"
else
  options=""
fi

kubectl-conf $TARGET_ENV $options
$(aws ecr get-login --no-include-email --region us-east-1)
exec python deployer/app.py "$@"
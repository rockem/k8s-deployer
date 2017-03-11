#!/bin/sh
AWS_REGISTRY='911479539546.dkr.ecr.us-east-1.amazonaws.com'
APP_IMAGE='deployer-test-restless:1.0'

docker build -t $APP_IMAGE .
docker tag $APP_IMAGE $AWS_REGISTRY/$APP_IMAGE
docker push $AWS_REGISTRY/$APP_IMAGE

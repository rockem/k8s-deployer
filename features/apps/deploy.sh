#!/bin/sh

APP_IMAGE=911479539546.dkr.ecr.us-east-1.amazonaws.com/deployer-test-healthy:1.0

docker build $APP_IMAGE .
docker push $APP_IMAGE

#!/bin/sh

version=$1
if [[ -z "$version" ]]; then
    echo 'usage: ./deploy.sh <version>'
    exit 1
fi

AWS_REGISTRY='911479539546.dkr.ecr.us-east-1.amazonaws.com'
APP_IMAGE="deployer-test-stateful:$version"

echo $APP_IMAGE
docker build --build-arg VERSION=$version -t $APP_IMAGE .
docker tag $APP_IMAGE $AWS_REGISTRY/$APP_IMAGE
docker push $AWS_REGISTRY/$APP_IMAGE

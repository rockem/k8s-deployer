#!/usr/bin/env bash
docker build -t service_stub .
docker tag service_stub 911479539546.dkr.ecr.us-east-1.amazonaws.com/k8s-platform:service_stub
docker push 911479539546.dkr.ecr.us-east-1.amazonaws.com/k8s-platform
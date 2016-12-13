#!/usr/bin/env bash
echo "build docker image"
docker build -t k8s-deployer .
echo "tag image"
docker tag k8s-deployer:latest 911479539546.dkr.ecr.us-east-1.amazonaws.com/k8s-deployer:latest
echo "push image"
docker push 911479539546.dkr.ecr.us-east-1.amazonaws.com/k8s-deployer:latest

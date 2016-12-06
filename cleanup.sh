#!/usr/bin/env bash
echo "remove un needed docker images"
docker rmi $(docker images | grep "^<none>" | awk '{print $3}')
echo "kill docker processes"
docker rm $(docker ps -a -q)
echo "build docker image"
docker build -t deploy .
echo "start docker"
docker run -v /var/run/docker.sock:/var/run/docker.sock -e IMAGE_NAME=911479539546.dkr.ecr.us-east-1.amazonaws.com/k8s.workshop.registry:latest -t deploy
#!/bin/sh
docker version && $(aws ecr get-login --region us-east-1) && cd /opt/deployer && python deployer/deployer.py "$@"
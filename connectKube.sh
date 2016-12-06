#!/usr/bin/env bash
rm -rf ./.cfssl/*
 rm -rf config
 aws s3 sync s3://agt-terraform-state-prod/config-amazia/cfssl .cfssl
 aws s3 sync s3://agt-terraform-state-prod/config-amazia/k8s-structs .
 cp ~/.kube/config ~/.kube/config_back
 cp config ~/.kube/
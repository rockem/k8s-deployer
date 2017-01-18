import getpass
import os
import re
import subprocess
import time

import requests
from behave import *
from flask import json

use_step_matcher("re")

TARGET_ENV = 'int' # param from feature file?
HEALTHY_NAME = "healthy-" + getpass.getuser() + "-" + str(int(time.time()))
AWS_ACCESS_KEY = 'AKIAJUHGHBF4SEHXKLZA'
AWS_SECRET_KEY = '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'
REPO_NAME = 'behave_repo'
GIT_REPO = "file://" + os.getcwd() + '/' + REPO_NAME
AWS_REGISTRY_URI = "911479539546.dkr.ecr.us-east-1.amazonaws.com"
PUSHER_IMAGE_NAME = AWS_REGISTRY_URI + '/pusher:latest'
HEALTHY_SERVICE_IMAGE_NAME = AWS_REGISTRY_URI + '/' + HEALTHY_NAME

@given("login")
def login(context):
    subprocess.check_output('$(aws ecr get-login --region us-east-1)', shell=True)

@when("deploy (.*)? service(?: should (.*))?")
def deploy_healthy_service(context, name, status):
    image_name = __get_service_image_name(name)
    __docker_build(image_name, "./features/%s/." % name)
    __upload_to_registry(name)
    assert __deploy(image_name) == (status != 'fail') , 'failed to deploy'

@then("healthy service still serving")
def healthy_service_is_serving(context):
    __wait_for_service_deploy()
    __wait_for_service_to_be_available_k8s()


def __wait_for_service_to_be_available_k8s():
    service_up = False
    counter = 0
    while counter < 120:
        counter =+1
        output = subprocess.check_output("kubectl describe services %s" % HEALTHY_NAME, shell=True)
        print output
        match = re.search(r"LoadBalancer Ingress:\s(.*)", output)
        if match:
            result = match.group(1)
            print 'found a match -> %s' % result
            try:
                o = requests.get('http://' + result + "/health")
                print 'this is the service output %s' %o
                assert json.loads(o.text)['status']['code'] == 'UP', 'Healthy service not serving anymore'
                service_up = True
                break
            except requests.exceptions.ConnectionError as e:
                print '%s is not ready yet, going to sleep and run for another try' % result
                time.sleep(1)
        else:
            print 'didnt found a match, going to sleep and run for another try'
            time.sleep(1)

    if not service_up:
        raise Exception('The service in k8s probably did not start')

def __wait_for_service_deploy():
    counter = 0
    while counter < 120:
        counter =+1
        if  __is_running():
            return
        time.sleep(1)

    raise Exception('The service in k8s probably did not start')


def __is_running():
    output = subprocess.check_output("kubectl describe pods %s" % HEALTHY_NAME, shell=True)
    match = re.search(r"Status:\s(.*)", output)
    if match:
        result = match.group(1)
        if result.strip() == 'Running':
            return True
    return False

def __get_service_image_name(version):
    return HEALTHY_SERVICE_IMAGE_NAME + ':' + version

def __upload_to_registry(version):
        subprocess.check_output('docker pull ' + PUSHER_IMAGE_NAME +
                                ' && docker run -v' + ' /var/run/docker.sock:/var/run/docker.sock -e KEY_ID=' +
                                AWS_ACCESS_KEY + ' -e ACCESS_KEY=' + AWS_SECRET_KEY + ' -e IMAGE_NAME=' +
                                HEALTHY_SERVICE_IMAGE_NAME + ":" + version + ' ' + PUSHER_IMAGE_NAME, shell=True)

def __deploy(name):
    return os.system(
        "python deployer/deployer.py deploy --image_name %s --target %s "
        "--git_repository %s" % (name, TARGET_ENV, GIT_REPO)) == 0

def __docker_build(name, location):
    comand = "docker build -t %s %s" % (name.strip(), location)
    os.system(comand)

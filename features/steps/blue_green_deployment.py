import getpass
import os
import re
import subprocess
import time

import requests
from behave import *
from flask import json

from features.steps.support import TARGET_ENV_AND_NAMESPACE, NAMESPACE

use_step_matcher("re")

TARGET_ENV = 'int'  # param from feature file?
AUTOGEN_SERVICE_NAME = "healthy-" + getpass.getuser() + "-" + str(int(time.time()))
AWS_ACCESS_KEY = 'AKIAJUHGHBF4SEHXKLZA'
AWS_SECRET_KEY = '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'
REPO_NAME = 'behave_repo'
GIT_REPO = "file://" + os.getcwd() + '/' + REPO_NAME
AWS_REGISTRY_URI = "911479539546.dkr.ecr.us-east-1.amazonaws.com"
PUSHER_IMAGE_NAME = AWS_REGISTRY_URI + '/pusher:latest'
AUTOGEN_SERVICE_IMAGE_NAME = AWS_REGISTRY_URI + '/' + AUTOGEN_SERVICE_NAME


@when("deploy \"(.*?)(?:\\:(\d+))?\" service(?: should (.*))?")
def deploy_healthy_service(context, name, version, status):
    image_name = __get_service_image_name(name)
    __docker_build(version, image_name, "./features/%s/." % name)
    __upload_to_registry(name)

    assert __deploy(image_name, __get_recipe_path(name)) == (status != 'fail'), 'failed to deploy'


def __get_recipe_path(name):
    path = "./features/%s/recipe.yml" % name
    if os.path.isfile(path):
        return os.path.realpath(path)


@then("healthy service still serving")
def healthy_service_is_serving(context):
    __wait_for_service_deploy()
    __wait_for_service_to_be_available_k8s()


def __validate_version_updated(domain, version):
    o = requests.get('http://' + domain + "/version")
    print ('service version output %s' % o)
    assert json.loads(o.text)['version'] == str(version), 'Healthy service not serving anymore'


@then("service updated to version (\d+)")
def service_updated(context, version):
    __wait_for_service_deploy()
    domain = __wait_for_service_to_be_available_k8s()
    __validate_version_updated(domain, version)


def __wait_for_service_to_be_available_k8s():
    service_up = False
    counter = 0
    result = None
    while counter < 120:
        counter = +1
        output = subprocess.check_output(
            "kubectl describe --namespace %s services %s" % (NAMESPACE, AUTOGEN_SERVICE_NAME), shell=True)
        print (output)
        match = re.search(r"LoadBalancer Ingress:\s(.*)", output)
        if match:
            result = match.group(1)
            print ('found a match -> %s' % result)
            try:
                o = requests.get('http://' + result + "/health")
                print ('this is the service output %s' % o)
                assert json.loads(o.text)['status']['code'] == 'UP', 'Healthy service not serving anymore'
                service_up = True
                break
            except requests.exceptions.ConnectionError as e:
                print ('%s is not ready yet, going to sleep and run for another try' % result)
                time.sleep(1)
        else:
            print ('didnt found a match, going to sleep and run for another try')
            time.sleep(1)

    if not service_up:
        raise Exception('The service in k8s probably did not start')

    return result


def __wait_for_service_deploy():
    counter = 0
    while counter < 120:
        counter = +1
        if __is_running():
            return
        time.sleep(1)

    raise Exception('The service in k8s probably did not start')


def __is_running():
    output = subprocess.check_output("kubectl describe --namespace %s pods %s" % (NAMESPACE, AUTOGEN_SERVICE_NAME),
                                     shell=True)
    match = re.search(r"Status:\s(.*)", output)
    if match:
        result = match.group(1)
        if result.strip() == 'Running':
            return True
    return False


def __get_service_image_name(version):
    return AUTOGEN_SERVICE_IMAGE_NAME + ':' + version


def __upload_to_registry(version):
    subprocess.check_output('docker run -v' + ' /var/run/docker.sock:/var/run/docker.sock -e KEY_ID=' +
                            AWS_ACCESS_KEY + ' -e ACCESS_KEY=' + AWS_SECRET_KEY + ' -e IMAGE_NAME=' +
                            AUTOGEN_SERVICE_IMAGE_NAME + ":" + version + ' ' + PUSHER_IMAGE_NAME, shell=True)


def __deploy(name, recipe_path=None):
    recipe_path = calc_recipe_path(recipe_path)
    return os.system(
        "python deployer/deployer.py deploy --image_name %s --target %s "
        "--git_repository %s %s" % (name, TARGET_ENV_AND_NAMESPACE, GIT_REPO, recipe_path)) == 0


def calc_recipe_path(recipe_path):
    recipe_path = '' if recipe_path is None else '--recipe %s' % recipe_path
    return recipe_path


def __docker_build(version, name, location):
    # comand = "docker build --build-arg VERSION=%s -t %s %s" % (version, name.strip(), location)
    if not version:
        build_arg = ""
    else:
        build_arg = '--build-arg VERSION=%s' % version

    comand = "docker build %s -t %s %s" % (build_arg, name.strip(), location)
    os.system(comand)

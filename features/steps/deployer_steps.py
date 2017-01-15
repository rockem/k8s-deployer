import getpass
import os
import subprocess
import time
from time import sleep

import requests
from behave import *
from requests.exceptions import ConnectionError
from deployer.log import DeployerLogger
from deployer.services import ServiceVersionWriter, ServiceVersionReader

use_step_matcher("re")
TARGET_ENV = 'int'
REPO_NAME = 'behave_repo'
GIT_REPO = "file://" + os.getcwd() + '/' + REPO_NAME
# GIT_REPO = 'https://git.dnsk.io/media-platform/k8s-services-envs'
# SERVICE_NAME = "deployer-stub-" + getpass.getuser() + "-" + str(int(time.time()))
# IMAGE_NAME = SERVICE_NAME + ":latest"
CONFIG_MAP = 'global-config'
AWS_REGISTRY_URI = "911479539546.dkr.ecr.us-east-1.amazonaws.com"
PUSHER_IMAGE_NAME = AWS_REGISTRY_URI + '/pusher:latest'
AWS_ACCESS_KEY = 'AKIAJUHGHBF4SEHXKLZA'
AWS_SECRET_KEY = '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'
JAVA_SERVICE_NAME = 'deployer-test-java-service-' + getpass.getuser() + "-" + str(int(time.time()))
JAVA_SERVICE_IMAGE_NAME = AWS_REGISTRY_URI + '/' + JAVA_SERVICE_NAME + ':0.1.0'

logger = DeployerLogger(__name__).getLogger()


# @given("service is dockerized")
# def dockerize(context):
#     os.system("docker build -t %s ./features/service_stub/." % SERVICE_NAME)


@when('deploying')
def deploy(context):
    # assert os.system(
    #     "python deployer/deployer.py deploy --image_name %s --target %s "
    #     "--git_repository %s" % (IMAGE_NAME, TARGET_ENV, GIT_REPO)) == 0
    logger.debug('deploy java service to k8s')
    subprocess.check_output("python deployer/deployer.py deploy --image_name %s --target %s --git_repository %s" %
                            (JAVA_SERVICE_IMAGE_NAME, TARGET_ENV, GIT_REPO), shell=True)

@then("service should be deployed( .*)?")
def should_be_deployed(context, env):
    output = os.popen("kubectl get svc %s" % JAVA_SERVICE_NAME).read()
    assert JAVA_SERVICE_NAME in output


@given("service is defined in source environment")
def write_service_to_int_git(context):
    ServiceVersionWriter(GIT_REPO).write('kuku', JAVA_SERVICE_NAME, JAVA_SERVICE_IMAGE_NAME)


@when("promoting to production")
def promote(context):
    assert os.system("python deployer/deployer.py promote --source kuku --target %s "
                     "--git_repository %s" % (TARGET_ENV, GIT_REPO)) == 0


@then("service should be logged in git")
def check_promoted_service_in_git(context):
    assert ServiceVersionReader(GIT_REPO).read(TARGET_ENV)[0] == JAVA_SERVICE_IMAGE_NAME


def update_k8s_configuration():
    os.popen("kubectl delete configmap global-config")
    subprocess.check_output("kubectl create configmap global-config --from-file=%s" % os.getcwd() +
                            '/features/config/global.yml', shell=True)


# @when("a new java service is deployed to k8s")
# def deploy_java_service(context):
#     logger.debug('deploy java service to k8s')
#     subprocess.check_output(
#         "python deployer/deployer.py deploy --image_name %s --target %s "
#         "--git_repository %s" % (JAVA_SERVICE_IMAGE_NAME, TARGET_ENV, GIT_REPO), shell=True)


def upload_java_image_to_registry():
    __build()
    __dockerize_java()
    __login()
    __upload_to_docker_registry()


def delete_java_image_from_registry():
    os.popen('docker rmi -f %s' % JAVA_SERVICE_IMAGE_NAME)
    os.popen('aws ecr delete-repository --force --repository-name %s' % JAVA_SERVICE_NAME)


def __build():
    logger.debug('building the service')
    subprocess.check_output('cd features/service && ./gradlew clean build', shell=True)


def __dockerize_java():
    logger.debug('dockerize the service')
    subprocess.check_output('cd features/service && ./gradlew dockerize '
                            '-PimageName=' + JAVA_SERVICE_IMAGE_NAME, shell=True)


def __login():
    logger.debug('login to aws')
    subprocess.check_output('$(aws ecr get-login --region us-east-1)', shell=True)


def __upload_to_docker_registry():
    logger.debug('uploading the service to aws registry')
    subprocess.check_output('docker pull ' + PUSHER_IMAGE_NAME +
                            ' && docker run -v' + ' /var/run/docker.sock:/var/run/docker.sock -e KEY_ID=' +
                            AWS_ACCESS_KEY + ' -e ACCESS_KEY=' + AWS_SECRET_KEY + ' -e IMAGE_NAME=' +
                            JAVA_SERVICE_IMAGE_NAME + ' ' + PUSHER_IMAGE_NAME, shell=True)


@then("the service should get the new configuration")
def get_configuration(context):
    logger.debug('waiting for the service deployment')
    svc_host = __wait_for_service_deploy()
    greeting = __get_greeting(svc_host, '/greeting')
    assert greeting == 'Hello overridden world'


def __wait_for_service_deploy():
    svc_host = None
    for _ in range(120):
        try:
            service_describe_output = subprocess.check_output("kubectl describe service %s" % JAVA_SERVICE_NAME,
                                                              shell=True)
            # e.g. LoadBalancer Ingress:	a31d2dc35d67311e6b4410e7feeb8c22-467957310.us-east-1.elb.amazonaws.com
            #      Port:			        <unset>	80/TCP
            lb_index = service_describe_output.find("LoadBalancer Ingress:")
            if lb_index == -1:
                sleep(1)
                continue
            svc_host = service_describe_output[lb_index + 22:service_describe_output.find("Port") - 1]
            __call_service(svc_host)
            break
        except ConnectionError:
            sleep(1)
    if svc_host is None:
        raise Exception('The service did not start after 120 seconds')
    return svc_host


def __call_service(svc_host):
    url = 'http://' + svc_host + '/health'
    health = requests.get(url).text
    logger.info('The service url is:%s, \nThe returned health is:%s' % (url, health))


def __get_greeting(svc_host, path):
    url = 'http://' + svc_host + path
    return requests.get(url).text


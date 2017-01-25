import getpass
import os
import shutil
import subprocess
import time

import git
from requests import ConnectionError

from deployer.log import DeployerLogger

REPO_NAME = 'behave_repo'
RANDOM_IDENTIFIER = getpass.getuser() + "-" + str(int(time.time()))
NAMESPACE = RANDOM_IDENTIFIER
TARGET_ENV = 'int'
TARGET_ENV_AND_NAMESPACE = TARGET_ENV + ':' + NAMESPACE
GIT_REPO_URL = "file://" + os.getcwd() + '/' + REPO_NAME
# GIT_REPO = "https://git.dnsk.io/media-platform/k8s-config"
# GIT_REPO = "git@git.dnsk.io:media-platform/k8s-config.git"


JAVA_SERVICE_NAME = "deployer-test-java-service-%s" % RANDOM_IDENTIFIER
AWS_REGISTRY_URI = "911479539546.dkr.ecr.us-east-1.amazonaws.com"
JAVA_SERVICE_IMAGE_NAME = AWS_REGISTRY_URI + '/' + JAVA_SERVICE_NAME + ':0.1.0'
AWS_ACCESS_KEY = 'AKIAJUHGHBF4SEHXKLZA'
AWS_SECRET_KEY = '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'
PUSHER_IMAGE_NAME = AWS_REGISTRY_URI + '/pusher:latest'

logger = DeployerLogger(__name__).getLogger()


def create_namespace(context):
    os.popen("kubectl create namespace %s" % NAMESPACE)
    context.config.userdata["namespace"] = NAMESPACE # why this trainwreck


def update_k8s_configuration():
    print("deleting configmap")
    os.popen("kubectl delete configmap global-config --namespace=%s" % NAMESPACE)
    print("creating configmap")
    subprocess.check_output(
        "kubectl create configmap global-config --from-file=global.yml=%s --namespace=%s" % (os.getcwd() +
                                                                                             '/features/config/common.yml',
                                                                                             NAMESPACE), shell=True)
    print("configmap created all is cool")


def delete_java_image_from_registry():
    os.popen('docker rmi -f %s' % JAVA_SERVICE_IMAGE_NAME)
    os.popen('aws ecr delete-repository --force --repository-name %s' % JAVA_SERVICE_NAME)


def create_repo():
    if os.path.exists(REPO_NAME):
        shutil.rmtree(REPO_NAME)
    repo = git.Repo()
    repo.init(REPO_NAME, bare=True)


def delete_java_service_from_k8s():
    logger.debug('deleting service and deployment from the current k8s env')
    os.popen("kubectl delete service %s" % JAVA_SERVICE_NAME)
    os.popen("kubectl delete deployment %s" % JAVA_SERVICE_NAME)


def upload_java_image_to_registry():
    __build()
    __dockerize_java()
    __upload_to_docker_registry()


def __build():
    logger.debug('building the service')
    subprocess.check_output('cd features/service && ./gradlew clean build', shell=True)


def __dockerize_java():
    logger.debug('dockerize the service')
    subprocess.check_output('cd features/service && ./gradlew dockerize '
                            '-PimageName=' + JAVA_SERVICE_IMAGE_NAME, shell=True)


def __upload_to_docker_registry():
    __login()
    logger.debug('uploading the service to aws registry')
    subprocess.check_output('docker pull ' + PUSHER_IMAGE_NAME +
                            ' && docker run -v' + ' /var/run/docker.sock:/var/run/docker.sock -e KEY_ID=' +
                            AWS_ACCESS_KEY + ' -e ACCESS_KEY=' + AWS_SECRET_KEY + ' -e IMAGE_NAME=' +
                            JAVA_SERVICE_IMAGE_NAME + ' ' + PUSHER_IMAGE_NAME, shell=True)


def __login():
    logger.debug('login to aws')
    subprocess.check_output('$(aws ecr get-login --region us-east-1)', shell=True)


def __busy_wait(run_func):
    returned_value = None
    for _ in range(120):
        try:
            returned_value = run_func()
            break
        except ConnectionError:
            time.sleep(1)
    if returned_value is None:
        raise Exception('The function %s did not return value after 120 seconds' % run_func)
    return returned_value


def delete_namespace(namespace):
    os.system("kubectl delete namespace %s" % namespace)
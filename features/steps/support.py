import os
import getpass
import time
import subprocess
import shutil

from deployer.gitclient.git_client import GitClient
from deployer.log import DeployerLogger

REPO_NAME = 'behave_repo'
RANDOM_IDENTIFIER = getpass.getuser() + "-" + str(int(time.time()))
NAMESPACE = RANDOM_IDENTIFIER
TARGET_ENV = 'int'
TARGET_ENV_AND_NAMESPACE = TARGET_ENV + ':' + NAMESPACE
GIT_REPO = "file://" + os.getcwd() + '/' + REPO_NAME
JAVA_SERVICE_NAME = "deployer-test-java-service-%s" % RANDOM_IDENTIFIER
AWS_REGISTRY_URI = "911479539546.dkr.ecr.us-east-1.amazonaws.com"
JAVA_SERVICE_IMAGE_NAME = AWS_REGISTRY_URI + '/' + JAVA_SERVICE_NAME + ':0.1.0'
AWS_ACCESS_KEY = 'AKIAJUHGHBF4SEHXKLZA'
AWS_SECRET_KEY = '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'
PUSHER_IMAGE_NAME = AWS_REGISTRY_URI + '/pusher:latest'

logger = DeployerLogger(__name__).getLogger()


def create_namespace():
    os.popen("kubectl create namespace %s" % NAMESPACE)


def update_k8s_configuration():
    os.popen("kubectl delete configmap global-config --namespace=%s" % NAMESPACE)
    subprocess.check_output("kubectl create configmap global-config --from-file=%s --namespace=%s" % (os.getcwd() +
                            '/features/config/global.yml', NAMESPACE), shell=True)


def delete_java_image_from_registry():
    os.popen('docker rmi -f %s' % JAVA_SERVICE_IMAGE_NAME)
    os.popen('aws ecr delete-repository --force --repository-name %s' % JAVA_SERVICE_NAME)


def create_repo():
    if os.path.exists(REPO_NAME):
        shutil.rmtree(REPO_NAME)
    GitClient().init(REPO_NAME)


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
import getpass
import os
import shutil
import subprocess
import time

import git
from requests import ConnectionError

from deployer.log import DeployerLogger
from features.support.app import AppDriver
from features.support.context import Context
from features.support.k8s import K8sDriver

REPO_NAME = 'behave_repo'
# RANDOM_IDENTIFIER = getpass.getuser() + "-" + str(int(time.time()))
# NAMESPACE = getpass.getuser() + "-" + str(int(time.time()))
TARGET_ENV = 'int'
# TARGET_ENV_AND_NAMESPACE = TARGET_ENV + ':' + NAMESPACE
GIT_REPO_URL = "file://" + os.getcwd() + '/' + REPO_NAME
# GIT_REPO = "https://git.dnsk.io/media-platform/k8s-config"
# GIT_REPO = "git@git.dnsk.io:media-platform/k8s-config.git"


JAVA_SERVICE_NAME = "deployer-test-java"
AWS_ACCESS_KEY = 'AKIAJUHGHBF4SEHXKLZA'
AWS_SECRET_KEY = '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'

logger = DeployerLogger(__name__).getLogger()

def get_target_environment(context):
    return TARGET_ENV + ':' +  Context(context).default_namespace()

def create_namespace(context):
    namespace = getpass.getuser() + "-" + str(int(time.time()))
    k8s = K8sDriver(namespace, context.minikube)
    k8s.create_namespace()
    Context(context).set_default_namespace(namespace)
    k8s.upload_config('default')


# def update_k8s_configuration():
#     print("deleting configmap")
#     os.popen("kubectl delete configmap global-config --namespace=%s" % NAMESPACE)
#     print("creating configmap")
#     subprocess.check_output(
#         "kubectl create configmap global-config --from-file=global.yml=%s --namespace=%s" % (os.getcwd() +
#                                                                                              '/features/config/common.yml',
#                                                                                              NAMESPACE), shell=True)
#     print("configmap created all is cool")


def create_repo():
    if os.path.exists(REPO_NAME):
        shutil.rmtree(REPO_NAME)
    repo = git.Repo()
    repo.init(REPO_NAME, bare=True)


def delete_java_service_from_k8s():
    logger.debug('deleting service and deployment from the current k8s env')
    os.popen("kubectl delete service %s" % JAVA_SERVICE_NAME)
    os.popen("kubectl delete deployment %s" % JAVA_SERVICE_NAME)


def __build():
    logger.debug('building the service')
    subprocess.check_output('cd features/service && ./gradlew clean build', shell=True)


def __login():
    logger.debug('login to aws')
    subprocess.check_output('$(aws ecr get-login --region us-east-1)', shell=True)


def __busy_wait(run_func, *args):
    returned_value = None
    for _ in range(120):
        try:
            returned_value = run_func(*args)
            break
        except ConnectionError:
            time.sleep(1)
    if returned_value is None:
        raise Exception('The function %s did not return value after 120 seconds' % run_func)
    return returned_value


def delete_namespace(namespace):
    os.system("kubectl delete ns --force %s" % namespace)

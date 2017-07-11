import getpass
import os
import shutil
import subprocess
import time
import git

from deployer.log import DeployerLogger
from features.support.context import Context
from features.support.k8s import K8sDriver

REPO_NAME = 'behave_repo'
TARGET_ENV = 'int'
GIT_REPO_URL = "file://" + os.getcwd() + '/' + REPO_NAME
JAVA_SERVICE_NAME = "deployer-test-java"
logger = DeployerLogger(__name__).getLogger()

def get_target_environment(context, namespace = None):
    return Context(context).default_namespace() if namespace == None else namespace

def create_namespace(context):
    namespace = getpass.getuser() + "-" + str(int(time.time()))
    k8s = K8sDriver(namespace, context.minikube)
    k8s.create_namespace()
    Context(context).set_default_namespace(namespace)
    k8s.upload_config('default')

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


def delete_namespace(namespace):
    os.system("kubectl delete ns --force %s" % namespace)

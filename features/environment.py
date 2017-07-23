import os

import subprocess
import getpass
import re

import time
import git
import shutil

from kubectlconf.kops import KopsSync
from kubectlconf.sync import S3ConfSync
from deployer.log import DeployerLogger
from features.support.context import Context
from features.support.docker import AppImageBuilder, JavaAppBuilder, AWSImagePusher, AppImage
from features.support.k8s import K8sDriver

JAVA_SERVICE_NAME = "deployer-test-java"
REPO_NAME = 'behave_repo'
TARGET_ENV = 'int'
GIT_REPO_URL = "file://" + os.getcwd() + '/' + REPO_NAME

logger = DeployerLogger(__name__).getLogger()

APP_BUILDERS = [
    AppImageBuilder('version', 'healthy', ['VERSION=healthy']),
    AppImageBuilder('version', 'sick', ['VERSION=sick']),
    AppImageBuilder('restless', '1.0'),
    JavaAppBuilder(AppImageBuilder('java', '1.0')),
    AppImageBuilder('version', '1.0', ['VERSION=1.0']),
    AppImageBuilder('version', '2.0', ['VERSION=2.0'])
]


def before_all(context):
    __build_apps(context)
    os.environ['TARGET_ENV'] = TARGET_ENV
    if __is_aws_mode(context):
        KopsSync(TARGET_ENV).sync()
        context.aws_uri = "911479539546.dkr.ecr.us-east-1.amazonaws.com/"
        context.minikube = None
        __push_apps_aws(Context(context).all_apps())
    else:
        context.minikube = subprocess.check_output('minikube ip', shell=True)[:-1]
        context.aws_uri = ''


def __build_apps(context):
    for b in APP_BUILDERS:
        app = b.build(__is_aws_mode(context))
        Context(context).add_app(app)

def __is_aws_mode(context):
    try:
        return context.config.userdata['mode'] == 'aws'
    except KeyError:
        return False


def __push_apps_aws(apps):
    for app in apps:
        AWSImagePusher(app).push()

def after_scenario(context, scenario):
    K8sDriver.delete_namespaces(Context(context).namespaces_to_delete())

def before_scenario(context, scenario):
    __create_namespace(context)
    __create_repo()
    __delete_java_service_from_k8s()

def __create_namespace(context):
    namespace = getpass.getuser() + "-" + str(int(time.time()))
    print ("namespace:%s" %(namespace))
    k8s = K8sDriver(namespace, context.minikube)
    k8s.create_namespace()
    Context(context).set_default_namespace(namespace)
    k8s.upload_config('default')

def __create_repo():
    if os.path.exists(REPO_NAME):
        shutil.rmtree(REPO_NAME)
    repo = git.Repo()
    repo.init(REPO_NAME, bare=True)

def __delete_java_service_from_k8s():
    logger.debug('deleting service and deployment from the current k8s env')
    os.popen("kubectl delete service %s" % JAVA_SERVICE_NAME)
    os.popen("kubectl delete deployment %s" % JAVA_SERVICE_NAME)



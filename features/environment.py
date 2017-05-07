import os

import subprocess
from kubectlconf.sync import S3ConfSync

from deployer.log import DeployerLogger
from features.steps.support import delete_namespace
from features.support.context import Context
from features.support.docker import AppImageBuilder, JavaAppBuilder, AWSImagePusher, AppImage
from features.support.k8s import K8sDriver
from steps.support import create_namespace, delete_java_service_from_k8s, create_repo, \
    update_k8s_configuration, GIT_REPO_URL, TARGET_ENV

logger = DeployerLogger(__name__).getLogger()

APP_BUILDERS = [
    AppImageBuilder('healthy', '1.0'),
    AppImageBuilder('sick', '1.0'),
    AppImageBuilder('restless', '1.0'),
    JavaAppBuilder(AppImageBuilder('java', '1.0')),
    AppImageBuilder('version', '1.0', ['VERSION=1.0']),
    AppImageBuilder('version', '2.0', ['VERSION=2.0'])
]


def before_all(context):
    __build_apps(context)
    if __is_aws_mode(context):
        S3ConfSync(TARGET_ENV).sync()
        context.aws_uri = "911479539546.dkr.ecr.us-east-1.amazonaws.com/"
        context.minikube = None
        __push_apps_aws(Context(context).all_apps())
    else:
        context.minikube = subprocess.check_output('minikube ip', shell=True)[:-1]
        context.aws_uri = ''
    create_namespace(context)


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


def after_all(context):
    delete_namespace(context.config.userdata["namespace"])
    K8sDriver.delete_namespaces(Context(context).namespaces_to_delete())


def before_scenario(context, scenario):
    create_repo()
    delete_java_service_from_k8s()


def get_local_config_file_path():
    abs_file_path = os.getcwd() + "/features/config/global.yml"
    return abs_file_path

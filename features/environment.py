import os

import subprocess
from kubectlconf.sync import S3ConfSync

from deployer.log import DeployerLogger
from features.steps.configurer_steps import ConfigFilePusher
from features.steps.support import delete_namespace
from features.support.docker import AppPusher, JavaAppPusher
from steps.support import create_namespace, delete_java_service_from_k8s, delete_java_image_from_registry, create_repo, \
    update_k8s_configuration, upload_java_image_to_registry, GIT_REPO_URL, TARGET_ENV

logger = DeployerLogger(__name__).getLogger()


def before_all(context):
    # S3ConfSync(TARGET_ENV).sync()
    create_namespace(context)
    __push_apps()
    context.minikube = subprocess.check_output('minikube ip', shell=True)[:-1]
    # upload_java_image_to_registry()


def __push_apps():
    AppPusher('healthy', '1.0').push()
    AppPusher('sick', '1.0').push()
    AppPusher('restless', '1.0').push()
    JavaAppPusher(AppPusher('java', '1.0')).push()
    AppPusher('version', '1.0').push('VERSION=1.0')
    AppPusher('version', '2.0').push('VERSION=2.0')


def after_all(context):
    delete_namespace(context.config.userdata["namespace"])
    # delete_java_image_from_registry()


def before_scenario(context, scenario):
    create_repo()
    delete_java_service_from_k8s()
    if scenario.feature.name == 'Update k8s configuration':
        ConfigFilePusher(GIT_REPO_URL).write(TARGET_ENV, get_local_config_file_path())
    else:
        update_k8s_configuration()


def get_local_config_file_path():
    abs_file_path = os.getcwd() + "/features/config/global.yml"
    return abs_file_path

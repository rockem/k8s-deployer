import os

import subprocess
from kubectlconf.sync import S3ConfSync

from deployer.log import DeployerLogger
from features.steps.configurer_steps import ConfigFilePusher
from features.steps.support import delete_namespace
from features.support.docker import AppImageBuilder, JavaAppBuilder
from steps.support import create_namespace, delete_java_service_from_k8s, delete_java_image_from_registry, create_repo, \
    update_k8s_configuration, upload_java_image_to_registry, GIT_REPO_URL, TARGET_ENV

logger = DeployerLogger(__name__).getLogger()

APP_BUILDERS = [
    AppImageBuilder({'name': 'healthy', 'version': '1.0'}),
    AppImageBuilder({'name': 'sick', 'version': '1.0'}),
    AppImageBuilder({'name': 'restless', 'version': '1.0'}),
    JavaAppBuilder(AppImageBuilder({'name': 'java', 'version': '1.0'})),
    AppImageBuilder({'name': 'version', 'version': '1.0', 'args': ['VERSION=1.0']}),
    AppImageBuilder({'name': 'version', 'version': '2.0', 'args': ['VERSION=2.0']})
]


def before_all(context):
    if __is_aws_mode(context):
        S3ConfSync(TARGET_ENV).sync()
    create_namespace(context)
    __push_apps(__is_aws_mode(context))
    context.minikube = subprocess.check_output('minikube ip', shell=True)[:-1]
    # upload_java_image_to_registry()


def __is_aws_mode(context):
    try:
        return context.config.userdata['mode'] is 'aws'
    except KeyError:
        return False


def __push_apps(aws_mode):
    for b in APP_BUILDERS:
        b.build(aws_mode)


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

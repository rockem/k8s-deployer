import os

from kubectlconf.sync import S3ConfSync

from deployer.log import DeployerLogger
from features.steps.configurer_steps import delete_namespace, ConfigFilePusher
from steps.support import create_namespace, delete_java_service_from_k8s, delete_java_image_from_registry, create_repo, \
    update_k8s_configuration, upload_java_image_to_registry, GIT_REPO_URL, TARGET_ENV

logger = DeployerLogger(__name__).getLogger()


def before_all(context):
    S3ConfSync(TARGET_ENV).sync()
    create_namespace(context)
    upload_java_image_to_registry()


def before_feature(context, feature):
    update_k8s_configuration()


def after_all(context):
    delete_namespace(context)
    delete_java_image_from_registry()


def before_scenario(context, scenario):
    create_repo()
    delete_java_service_from_k8s()


def before_tag(context, tag):
    if tag == 'pushed_global_config':
        # pass
        ConfigFilePusher(GIT_REPO_URL).write(TARGET_ENV, get_local_config_file_path())



def get_local_config_file_path():
    abs_file_path = os.getcwd() + "/features/config/global.yml"
    return abs_file_path


def after_scenario(context, scenario):
    if 'service is created in a namespace' == scenario.name:
        delete_namespace(context, 'non-existing-namespace')

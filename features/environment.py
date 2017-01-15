import os
import shutil
from deployer.gitclient.git_client import GitClient
from deployer.log import DeployerLogger
from features.steps import deployer_steps
from features.steps.deployer_steps import REPO_NAME, upload_java_image_to_registry, delete_java_image_from_registry, \
    update_k8s_configuration, create_namespace

logger = DeployerLogger(__name__).getLogger()


def before_all(context):
    create_namespace()
    update_k8s_configuration()
    upload_java_image_to_registry()


# def after_all(context):
    # delete_namespace
    # delete_java_image_from_registry()


def before_scenario(context, scenario):
    delete_repo()
    GitClient().init(REPO_NAME)
    delete_k8s()


def delete_k8s():
    logger.debug('deleting service and deployment from the current k8s env')
    os.popen("kubectl delete service %s" % deployer_steps.JAVA_SERVICE_NAME)
    os.popen("kubectl delete deployment %s" % deployer_steps.JAVA_SERVICE_NAME)


def delete_repo():
    if os.path.exists(REPO_NAME):
        shutil.rmtree(REPO_NAME)


def after_scenario(context, scenario):
    delete_repo()

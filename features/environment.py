import os
import shutil
from deployer.gitclient.git_client import GitClient
from deployer.log import DeployerLogger
from features.steps import deployer_steps
from features.steps.deployer_steps import REPO_NAME

logger = DeployerLogger(__name__).getLogger()


def before_scenario(context, scenario):
    delete_repo()
    GitClient().init(REPO_NAME)
    delete_k8s()


def delete_k8s():
    logger.debug('deleting service and deployment from the current k8s env')
    os.popen("kubectl delete service %s" % deployer_steps.SERVICE_NAME)
    os.popen("kubectl delete deployment %s" % deployer_steps.SERVICE_NAME)
    os.popen("kubectl delete service %s" % deployer_steps.JAVA_SERVICE_NAME)
    os.popen("kubectl delete deployment %s" % deployer_steps.JAVA_SERVICE_NAME)
    os.popen("kubectl delete configmap %s" % deployer_steps.CONFIG_MAP)


def delete_repo():
    if os.path.exists(REPO_NAME):
        shutil.rmtree(REPO_NAME)


def after_scenario(context, scenario):
    delete_repo()
    # delete_k8s()

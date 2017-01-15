import os

from gitclient.git_client import GitClient
from k8sDeployer import K8sDeployer
from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class DeployRunner(object):
    git_client = GitClient()

    def deploy(self, ymls, namespace):
        NamespaceCreator(namespace).create()
        for yml in ymls:
            K8sDeployer().deploy(yml).to(namespace)


class NamespaceCreator(object):

    def __init__(self, namespace):
        self.namespace = namespace

    def create(self):
        os.popen("kubectl create namespace %s" % self.namespace)

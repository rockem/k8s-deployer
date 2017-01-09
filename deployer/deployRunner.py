from gitclient.git_client import GitClient
from k8sDeployer import K8sDeployer
from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class DeployRunner(object):
    git_client = GitClient()

    def deploy(self, ymls):
        for yml in ymls:
            K8sDeployer().deploy(yml).to()


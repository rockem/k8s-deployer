from gitclient.git_client import GitClient
from k8sDeployer import K8sDeployer
from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class DeployRunner(object):
    CHECKOUT_DIRECTORY = 'tmp'
    SERVICES_ENVS_REPO = 'https://git.dnsk.io/media-platform/k8s-services-envs'
    SERVICES_FOLDER = '/services/'
    IMAGE_NAME = 'image_name'
    git_client = GitClient()

    def deploy(self, ymls):
        for yml in ymls:
            K8sDeployer().deploy(yml).to()


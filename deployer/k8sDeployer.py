import os

from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class K8sNotAvailableError(Exception):
    K8S_NOT_RESPONDING_MSG = "k8s is not responding to ping"

    def __init(self):
        super(K8sNotAvailableError, self).__init__(self.K8S_NOT_RESPONDING_MSG)

class K8sDeployer(object):
    def __init__(self, connector):
        self.connector = connector

    def deploy(self, toDeploy):
        logger.debug("%s is a deployment/upgrade candidate" % toDeploy)
        self.sourceToDeploy = os.path.join('deployer/produce/' + toDeploy)
        return self

    def to(self):
        self.connector.cluster_info()
        self.connector.apply(self.sourceToDeploy)

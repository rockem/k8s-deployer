import os
import subprocess

from deployerLogger import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class k8sNotAvailableError(Exception):
    K8S_NOT_RESPONDING_MSG = "k8s is not responding to ping"

    def __init(self):
        super(k8sNotAvailableError, self).__init__(self.K8S_NOT_RESPONDING_MSG)

class K8sDeployer(object):

    def __ping_k8s(self):
        returned_code = subprocess.call("kubectl cluster-info", shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        if returned_code != 0:
            raise k8sNotAvailableError()

    def deploy(self, toDeploy):
        logger.debug("%s is a deployment candidate" %(toDeploy))
        self.sourceToDeploy = os.path.join('deployer/produce/' + toDeploy)
        return self

    def to(self):
        self.__ping_k8s()

        try:
            logger.info("Trying to upgrade %s" % self.sourceToDeploy)
            subprocess.call("kubectl replace -f " + self.sourceToDeploy, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
            logger.info("%s upgrade finished successfully" % self.sourceToDeploy)
            return
        except Exception:
            logger.info("failed to upgrade, probably a new installation, deploying %s" % self.sourceToDeploy)
            subprocess.call("kubectl create -f " + self.sourceToDeploy + " --validate=false --record", shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info("%s deployment finished successfully" % self.sourceToDeploy)
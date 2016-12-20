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
        logger.debug("%s is a deployment candidate" % toDeploy)
        self.sourceToDeploy = os.path.join('deployer/produce/' + toDeploy)
        return self

    def to(self):
        self.__ping_k8s()

        try:
            logger.info("deploying/upgrading %s" % self.sourceToDeploy)
            cmd = "kubectl apply --record -f " + self.sourceToDeploy
            logger.info("running '%s'" % cmd)
            error_code = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
            if error_code == 1:
                logger.info("deploying/upgrading of %s finished with error" % self.sourceToDeploy)
        except Exception as e:
            logger.exception(e)

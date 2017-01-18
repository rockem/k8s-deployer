import os
import re
import subprocess

from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class k8sNotAvailableError(Exception):
    K8S_NOT_RESPONDING_MSG = "k8s is not responding to ping"

    def __init(self):
        super(k8sNotAvailableError, self).__init__(self.K8S_NOT_RESPONDING_MSG)

class K8sDeployer(object):

    def __ping_k8s(self):
        self.__run("kubectl cluster-info")

    def deploy(self, toDeploy):
        logger.debug("%s is a deployment/upgrade candidate" % toDeploy)
        self.sourceToDeploy = os.path.join('deployer/produce/' + toDeploy)
        return self

    def to(self):
        self.__ping_k8s()

        cmd = "kubectl apply --validate=false --record -f " + self.sourceToDeploy
        logger.info("running '%s'" % cmd)
        self.__run(cmd)

    def __run(self, cmd):
        subprocess.check_output(cmd, shell=True)

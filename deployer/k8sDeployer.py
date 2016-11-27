import os


class k8sNotAvailableError(Exception):
    K8S_NOT_RESPONDING_MSG = "k8s is not responding to ping"

    def __init(self):
        super(k8sNotAvailableError, self).__init__(self.K8S_NOT_RESPONDING_MSG)

class K8sDeployer(object):

    def __ping_k8s(self):
        output = os.popen("kubectl get svc").read()
        if "kubernetes" not in output:
            raise k8sNotAvailableError()

    def deploy(self, toDeploy):
        self.sourceToDeploy = os.path.join('deployer/produce/' + toDeploy)
        return self

    def to(self, target): #TODO -> use target. for now default
        self.__ping_k8s()
        os.popen("kubectl delete -f " + self.sourceToDeploy)
        os.popen("kubectl create -f " + self.sourceToDeploy)
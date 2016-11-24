import os

K8S_NOT_RESPONDING = "k8s not responding to ping"


class k8sNotAvailableError(Exception):

    def __init(self):
        super(k8sNotAvailableError, self).__init__(K8S_NOT_RESPONDING)

class K8sDeployer(object):

    error_message = K8S_NOT_RESPONDING

    def __init__(self, sourceToDeploy, targetEnv):
        self.sourceToDeploy = sourceToDeploy
        self.targetEnv = targetEnv

    def __ping_k8s(self):
        output = os.popen("kubectl get svc").read()
        if "kubernetes" not in output:
            raise k8sNotAvailableError(self.error_message)

    def deploy_to_k8s(self):
        self.__ping_k8s()
        os.popen("kubectl delete -f " + self.sourceToDeploy)
        os.popen("kubectl create -f " + self.sourceToDeploy)

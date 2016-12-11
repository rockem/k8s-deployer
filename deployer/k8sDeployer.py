import os


class k8sNotAvailableError(Exception):
    K8S_NOT_RESPONDING_MSG = "k8s is not responding to ping"

    def __init(self):
        super(k8sNotAvailableError, self).__init__(self.K8S_NOT_RESPONDING_MSG)

class K8sDeployer(object):

    def __ping_k8s(self):
        output = os.popen("kubectl cluster-info").read()
        if "kubernetes" not in output:
            raise k8sNotAvailableError()

    def deploy(self, toDeploy):
        print "%s is a deployment candidate" %(toDeploy)
        self.sourceToDeploy = os.path.join('deployer/produce/' + toDeploy)
        return self

    def to(self):
        self.__ping_k8s()

        try:
            os.popen("kubectl delete -f " + self.sourceToDeploy)
        except Exception:
            print "first time service deployed"

        print "deploying %s" %(self.sourceToDeploy)
        os.popen("kubectl create -f " + self.sourceToDeploy + " --validate=false")
        print "%s deployment finished successfully" %(self.sourceToDeploy)
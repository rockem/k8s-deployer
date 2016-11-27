from k8sDeployer import K8sDeployer

class deployRunner(object):

    def __init__(self, target):
        self.target = target


    def deploy(self, ymls = []):
        for yml in ymls:
            K8sDeployer().deploy(yml).to(self.target)
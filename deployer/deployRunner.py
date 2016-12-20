from k8sDeployer import K8sDeployer

class deployRunner(object):

    def deploy(self, ymls = []):
        for yml in ymls:
            K8sDeployer().deploy(yml).to()

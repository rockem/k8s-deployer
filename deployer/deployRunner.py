from configuration_generator import ConfigurationGenerator
from k8sDeployer import K8sDeployer
from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class DeployRunner(object):

    def __init__(self, configuration):
        self.configuration = configuration

    def deploy(self, elements):
        for element in elements:
            K8sDeployer().deploy(self.__generate_element(str(element))).to()

    def __generate_element(self, element):
        ConfigurationGenerator(self.configuration).generate('deployer/produce/%s.yml'%element).by_template('deployer/orig/%s.yml'%element)
        return '%s.yml' %element

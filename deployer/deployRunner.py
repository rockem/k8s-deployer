from configuration_generator import ConfigurationGenerator
from k8sDeployer import K8sDeployer
from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class DeployRunner(object):
    def __init__(self, connector):
        self.connector = connector

    def deploy(self, configuration, elements):
        for element in elements:
            logger.debug("element : {}".format(element))
            K8sDeployer(self.connector).deploy(self.__generate_element(configuration, str(element))).to()

    def __generate_element(self, configuration, element):
        ConfigurationGenerator(configuration).generate('deployer/produce/%s.yml'%element).by_template('deployer/orig/%s.yml'%element)
        return '%s.yml' %element

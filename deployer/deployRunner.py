import os
from configuration_generator import ConfigurationGenerator
from k8sDeployer import K8sDeployer
from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class DeployRunner(object):

    def deploy(self, configuration, elements, namespace):
        NamespaceCreator(namespace).create()
        for element in elements:
            K8sDeployer().deploy(self.__generate_element(configuration, str(element))).to(namespace)

    def __generate_element(self, configuration, element):
        ConfigurationGenerator(configuration).generate('deployer/produce/%s.yml'%element).by_template('deployer/orig/%s.yml'%element)
        return '%s.yml' %element

class NamespaceCreator(object):

    def __init__(self, namespace):
        self.namespace = namespace

    def create(self):
        os.popen("kubectl create namespace %s" % self.namespace)

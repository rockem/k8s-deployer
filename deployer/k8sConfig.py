from configuration_generator import ConfigurationGenerator
from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class k8sConfig(object):

    def by(self, configuration):
        ConfigurationGenerator(configuration).generate('deployer/produce/deployment.yml').by_template('deployer/orig/deployment.yml')
        ConfigurationGenerator(configuration).generate('deployer/produce/service.yml').by_template('deployer/orig/service.yml')
        return ['deployment.yml', 'service.yml']


    def service_by(self, configuration):
        print 'this is the configuration for service.yml only : %s' %   configuration
        ConfigurationGenerator(configuration).generate('deployer/produce/service.yml').by_template('deployer/orig/service.yml')
        return ['service.yml']
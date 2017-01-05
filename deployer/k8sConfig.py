import os
import yaml
from configuration_generator import ConfigurationGenerator
from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class k8sConfig(object):

    def by(self, configuration):
        ConfigurationGenerator(configuration).generate('deployer/produce/deployment.yml').by_template('deployer/orig/deployment.yml')
        ConfigurationGenerator(configuration).generate('deployer/produce/service.yml').by_template('deployer/orig/service.yml')
        return ['deployment.yml', 'service.yml']

    def fetch_service_configuration_from_docker(self, image_name):
        logger.debug("fetch service configuration by running image %s" % image_name)
        configuration = os.popen("docker run " + image_name + " cat /opt/app/config.yml").read()
        logger.debug("configuration deployer should build yml's according to -> %s" % configuration)
        logger.debug("service configuration fetched for %s" % image_name)
        return yaml.load(configuration)

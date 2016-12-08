import os

import yaml

from configuration_generator import ConfigurationGenerator

class k8sConfig(object):

    def by(self, image_name):
        configuration = self.fetch_service_configuration_from_docker(image_name)
        ConfigurationGenerator(configuration).generate('deployer/produce/deployment.yml').by_template('deployer/orig/deployment.yml')
        ConfigurationGenerator(configuration).generate('deployer/produce/service.yml').by_template('deployer/orig/service.yml')
        return ['deployment.yml','service.yml']

    def fetch_service_configuration_from_docker(self, image_name):
        configuration = os.popen("docker run " + image_name + " cat /opt/app/config.yml").read()
        print configuration
        return yaml.load(configuration)
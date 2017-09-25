import os

import yaml

from deployer.k8s import DeployDescriptorFactory


class TestDeployDescriptorFactory:
    def __init__(self):
        pass

    TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'orig')

    def test_add_fluentd_definition(self):
        factory = DeployDescriptorFactory(self.TEMPLATE_PATH, {'logging': 'log4j', 'name': 'kuku'})
        with open(factory.deployment(), 'r') as f:
            assert self.is_fluentd_exists_in(yaml.load(f))

    def is_fluentd_exists_in(self, y):
        for c in y['spec']['template']['spec']['containers']:
            if c.has_key('fluentd') and c['fluentd']['image'] == 'fluentd':
                return True
        return False

    def test_add_port_definition_to_deployment(self):
        factory = DeployDescriptorFactory(self.TEMPLATE_PATH, {'ports': ['50:5000'], 'name': 'kuku'})
        with open(factory.deployment(), 'r') as f:
            deployment = yaml.load(f)
            ports = deployment['spec']['template']['spec']['containers'][0]['ports']
            assert {'containerPort': 5000} in ports

    def test_add_port_definition_to_service(self):
        factory = DeployDescriptorFactory(self.TEMPLATE_PATH, {'serviceColor': 'green', 'ports': ['50:5000']})
        with open(factory.service(), 'r') as f:
            ports = yaml.load(f)['spec']['ports']
            assert {'targetPort': 5000, 'port': 50} in ports



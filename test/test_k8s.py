import os

import yaml

from deployer.k8s import K8sDescriptorFactory


class TestK8sDescriptorFactory:
    def __init__(self):
        pass

    TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'orig')

    def test_add_port_definition_to_deployment(self):
        factory = K8sDescriptorFactory(self.TEMPLATE_PATH, {'ports': ['50:5000'], 'name': 'kuku'})
        with open(factory.deployment(), 'r') as f:
            deployment = yaml.load(f)
            ports = deployment['spec']['template']['spec']['containers'][0]['ports']
            assert {'containerPort': 5000} in ports

    def test_add_port_definition_to_service(self):
        factory = K8sDescriptorFactory(self.TEMPLATE_PATH, {'serviceColor': 'green', 'ports': ['50:5000']})
        with open(factory.service(), 'r') as f:
            ports = yaml.load(f)['spec']['ports']
            assert {'targetPort': 5000, 'port': 50} in ports


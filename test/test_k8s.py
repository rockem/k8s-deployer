import os

import yaml

from deployer import k8s
from deployer.k8s import K8sDescriptorFactory
from deployer.recipe import Recipe




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

    def test_add_load_balancer_type_to_service(self):
        service_path = self.__create_service({'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_UI})
        self.__assert_service_type(service_path, k8s.LOAD_BALANCER_SERVICE)

    def test_add_cluster_ip_type_to_service(self):
        service_path = self.__create_service({'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_API})
        self.__assert_service_type(service_path, k8s.CLUSTER_IP_SERVICE)

    def test_add_default_type_to_service(self):
        service_path = self.__create_service({'serviceColor': 'green'})
        self.__assert_service_type(service_path, k8s.CLUSTER_IP_SERVICE)

    def __create_service(self, configuration):
        factory = K8sDescriptorFactory(self.TEMPLATE_PATH, configuration)
        return factory.service()

    def __assert_service_type(self, service_path, expected_type):
        with open(service_path, 'r') as f:
            service_type = yaml.load(f)['spec']['type']
            assert service_type == expected_type

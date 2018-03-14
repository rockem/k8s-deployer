import os
import json
import yaml

from deployer import k8s
from deployer.k8s import K8sDescriptorFactory, AppExplorer
from deployer.recipe import Recipe


class ConnectorStub(object):
    def __init__(self):
        pass

    @staticmethod
    def describe_service(service_name):
        json.loads('Error from server (NotFound): services.extensions %s not found' % service_name)


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
        factory = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            {'serviceColor': 'green', 'ports': ['50:5000'], 'serviceType': Recipe.SERVICE_TYPE_UI})
        with open(factory.service(), 'r') as f:
            ports = yaml.load(f)['spec']['ports']
            assert {'targetPort': 5000, 'port': 50} in ports

    def test_add_internal_load_balancer_definition_to_service(self):
        internal_load_balancer_factory = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            {'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_LOCAL_UI})
        no_internal_load_balancer_factory = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            {'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_API})
        self.assert_internal_LB_in_annotations(internal_load_balancer_factory, '0.0.0.0/0')
        self.assert_internal_LB_in_annotations(no_internal_load_balancer_factory, None)

    @staticmethod
    def assert_internal_LB_in_annotations(factory, expected):
        with open(factory.service(), 'r') as f:
            annotations = yaml.load(f)['metadata']['annotations']
            key = 'service.beta.kubernetes.io/aws-load-balancer-internal'
            assert key in annotations and annotations[key] == expected

    def test_set_cluster_ip_type(self):
        service_path = self.__create_service({'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_API})
        self.__assert_service_type(service_path, k8s.CLUSTER_IP_SERVICE)

    def test_set_load_balancer_type_UI(self):
        service_path = self.__create_service({'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_UI})
        self.__assert_service_type(service_path, k8s.LOAD_BALANCER_SERVICE)

    def test_set_load_balancer_type_LOCAL_UI(self):
        service_path = self.__create_service({'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_LOCAL_UI})
        self.__assert_service_type(service_path, k8s.LOAD_BALANCER_SERVICE)

    def __create_service(self, configuration):
        factory = K8sDescriptorFactory(self.TEMPLATE_PATH, configuration)
        return factory.service()

    @staticmethod
    def __assert_service_type(service_path, expected_type):
        with open(service_path, 'r') as f:
            service_type = yaml.load(f)['spec']['type']
            assert service_type == expected_type

    def test_should_return_one_as_default_scale(self):
        assert AppExplorer(ConnectorStub()).get_deployment_scale("not_existing_service") == 1

    def test_should_return_desired_default_scale(self):
        assert AppExplorer(ConnectorStub()).get_deployment_scale("not_existing_service", 10) == 10

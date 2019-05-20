import json
import os
from subprocess import CalledProcessError

import yaml
from nose.tools import raises

from deployer import k8s
from deployer.k8s import K8sDescriptorFactory, AppExplorer, CpuCalculator, CpuLevelNotValid
from deployer.recipe import Recipe


class ConnectorStub(object):
    def __init__(self):
        pass

    def describe_deployment(self, deployment_name):
        raise CalledProcessError(0, None)

    @staticmethod
    def describe_service(service_name):
        json.loads('Error from server (NotFound): services.extensions %s not found' % service_name)


class AwsConnectorStub(object):
    CERTIFICATE = 'certificate'
    _domain = False

    def get_certificate_for(self, domain):
        self._domain = domain
        return self.CERTIFICATE

    def _called_with_domain(self):
        return self._domain


class TestK8sDescriptorFactory(object):
    AWS_CONNECTOR = AwsConnectorStub()
    TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'orig')
    PROPERTIES_FOR_UI_SERVICE = {'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_UI, 'domain': 'domain', 'ports': []}

    def test_add_port_definition_to_deployment(self):
        factory = K8sDescriptorFactory(self.TEMPLATE_PATH, {'ports': ['50:5000'], 'name': 'kuku'}, self.AWS_CONNECTOR)
        with open(factory.deployment(), 'r') as f:
            deployment = yaml.load(f)
            ports = deployment['spec']['template']['spec']['containers'][0]['ports']
            assert {'containerPort': 5000} in ports

    def test_should_add_admin_privelege_to_deployment_when_admin_privileges_set(self):
        factory = K8sDescriptorFactory(self.TEMPLATE_PATH, {'adminPrivileges': True, 'name': 'kuku'}, self.AWS_CONNECTOR)
        with open(factory.deployment(), 'r') as f:
            deployment = yaml.load(f)

            assert self.docker_volume_mount() in self.deployment_volume_mounts(deployment)
            assert self.docker_socket_volume() in self.spec_volumes(deployment)

    def test_should_not_add_admin_privelege_to_deployment_when_admin_privileges_not_set(self):
        factory = K8sDescriptorFactory(self.TEMPLATE_PATH, {'adminPrivileges': False, 'name': 'kuku'}, self.AWS_CONNECTOR)
        with open(factory.deployment(), 'r') as f:
            deployment = yaml.load(f)

            assert not self.docker_volume_mount() in self.deployment_volume_mounts(deployment)
            assert not self.docker_socket_volume() in self.spec_volumes(deployment)

    def test_should_create_autoscale(self):
        factory = K8sDescriptorFactory(self.TEMPLATE_PATH, {'autoScaleInfo':
                                                                {'minPods': 1, 'enabled': True, 'cpu': 'low', 'maxPods': 3}, 'name': 'kuku'}, self.AWS_CONNECTOR)

        with open(factory.autoscale(), 'r') as f:
            autoscale = yaml.load(f)
            assert autoscale['metadata']['name'] == 'kuku'
            assert autoscale['spec']['scaleTargetRef']['name'] == 'kuku'
            assert autoscale['spec']['minReplicas'] == 1
            assert autoscale['spec']['maxReplicas'] == 3
            assert autoscale['spec']['targetCPUUtilizationPercentage'] == 90


    def test_should_create_ingress(self):
        factory = K8sDescriptorFactory(self.TEMPLATE_PATH, {'ingressInfo':
                                                                {'enabled': True, 'host': 'mich.dev.io'}, 'serviceName': 'kuku'}, self.AWS_CONNECTOR)

        with open(factory.ingress(), 'r') as f:
            assert yaml.load(f)['spec']['rules'] == \
                   [{'host': 'mich.dev.io',
                     'http': {'paths': [{'path': '/', 'backend': {'serviceName': 'kuku', 'servicePort': 8080}}]}}]




    def docker_volume_mount(self):
        return {'mountPath': '/var/run/docker.sock', 'name': 'docker-socket-volume'}

    def deployment_volume_mounts(self, deployment):
        return deployment['spec']['template']['spec']['containers'][0]['volumeMounts']

    def docker_socket_volume(self):
        return {'hostPath': {'path': '/var/run/docker.sock', 'type': 'File'}, 'name': 'docker-socket-volume'}

    def spec_volumes(self, deployment):
        return deployment['spec']['template']['spec']['volumes']

    def test_add_port_definition_to_service(self):
        factory = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            {'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_API},
            self.AWS_CONNECTOR
        )
        with open(factory.service(), 'r') as f:
            ports = yaml.load(f)['spec']['ports']
            assert {'targetPort':8080, 'port': 80, 'name': 'tcp-80'} in ports

    def test_add_443_port_definition_to_ui_service(self):
        factory = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            self.PROPERTIES_FOR_UI_SERVICE,
            self.AWS_CONNECTOR)
        assert self.__assert_port_with_number(443, factory.service()) is True

    def test_add_80_port_definition_to_ui_service(self):
        factory = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            self.PROPERTIES_FOR_UI_SERVICE,
            self.AWS_CONNECTOR)
        assert self.__assert_port_with_number(80, factory.service()) is True

    def __assert_port_with_number(self, port_number, service_path):
        with open(service_path, 'r') as f:
            service_yml = yaml.load(f)
            ports = service_yml['spec']['ports']
            return {'targetPort': 8080, 'port': port_number, 'name': ('tcp-%s' % port_number)} in ports

    def __port_exists_in(self, port_number, port_entries):
        return [entry is not None
                for entry in port_entries
                if entry['port'] == port_number and entry['name'] == ('tcp-%s' % port_number)]

    def test_add_internal_load_balancer_definition_to_service(self):
        internal_load_balancer_factory = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            {'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_INTERNAL_UI},
            self.AWS_CONNECTOR)
        no_internal_load_balancer_factory = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            {'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_API},
            self.AWS_CONNECTOR)
        assert self.__assert_internal_LB_in_annotations(internal_load_balancer_factory.service()) is True
        assert self.__assert_internal_LB_in_annotations(no_internal_load_balancer_factory.service()) is False

    def test_add_external_load_balancer_definition_to_ui_service(self):
        external_load_balancer_factory = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            self.PROPERTIES_FOR_UI_SERVICE,
            self.AWS_CONNECTOR)
        no_external_load_balancer_factory = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            {'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_API},
            self.AWS_CONNECTOR)
        assert self.__assert_external_lb_in_annotations(external_load_balancer_factory.service()) is True
        assert self.__assert_external_lb_in_annotations(no_external_load_balancer_factory.service()) is False

    @staticmethod
    def __assert_external_lb_in_annotations(service_path):
        with open(service_path, 'r') as f:
            service_yml = yaml.load(f)
            annotations = service_yml['metadata']['annotations']
            key_ssl_cert = 'service.beta.kubernetes.io/aws-load-balancer-ssl-cert'
            key_ssl_port = 'service.beta.kubernetes.io/aws-load-balancer-ssl-ports'
            key_backend_port = 'service.beta.kubernetes.io/aws-load-balancer-backend-protocol'

            return all(key in annotations for key in (key_ssl_cert, key_ssl_port, key_backend_port))

    def test_certificate_was_set_to_ui_service(self):
        external_load_balancer_factory = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            self.PROPERTIES_FOR_UI_SERVICE,
            self.AWS_CONNECTOR)

        service_path = external_load_balancer_factory.service()
        assert self.AWS_CONNECTOR._called_with_domain() == ('*.%s' % self.PROPERTIES_FOR_UI_SERVICE['domain'])
        assert self.__assert_external_lb_has_certificate(service_path, self.AWS_CONNECTOR.CERTIFICATE)

    def __assert_external_lb_has_certificate(self, service_path, fetched_certificate):
        with open(service_path, 'r') as f:
            service_yml = yaml.load(f)
            return service_yml['metadata']['annotations'][
                       'service.beta.kubernetes.io/aws-load-balancer-ssl-cert'] == fetched_certificate

    def test_set_cluster_ip_type(self):
        service_path = self.__create_service({'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_API})
        self.__assert_service_type(service_path, k8s.CLUSTER_IP_SERVICE)

    def test_set_load_balancer_type_UI(self):
        service_path = self.__create_service(
            self.PROPERTIES_FOR_UI_SERVICE)
        self.__assert_service_type(service_path, k8s.LOAD_BALANCER_SERVICE)

    def test_set_load_balancer_type_LOCAL_UI(self):
        service_path = self.__create_service({'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_INTERNAL_UI})
        self.__assert_service_type(service_path, k8s.LOAD_BALANCER_SERVICE)

    def __create_service(self, configuration):
        factory = K8sDescriptorFactory(self.TEMPLATE_PATH,
                                       configuration,
                                       self.AWS_CONNECTOR)
        return factory.service()

    def test_metrics_should_be_disabled(self):
        service_path = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            {'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_INTERNAL_UI},
            self.AWS_CONNECTOR).service()
        assert self.__assert_prometheus_enabled(service_path) is False

    def test_metrics_should_be_enabled(self):
        service_path = K8sDescriptorFactory(
            self.TEMPLATE_PATH,
            {'serviceColor': 'green', 'serviceType': Recipe.SERVICE_TYPE_API,
             'metrics': {'enabled': True}}, self.AWS_CONNECTOR).service()
        assert self.__assert_prometheus_enabled(service_path) is True

    @staticmethod
    def __assert_service_type(service_path, expected_type):
        with open(service_path, 'r') as f:
            service_type = yaml.load(f)['spec']['type']
            assert service_type == expected_type

    @staticmethod
    def __assert_internal_LB_in_annotations(service_path):
        with open(service_path, 'r') as f:
            annotations = yaml.load(f)['metadata']['annotations']
            key = 'service.beta.kubernetes.io/aws-load-balancer-internal'
            return key in annotations

    @staticmethod
    def __assert_prometheus_enabled(service_path):
        with open(service_path, 'r') as f:
            annotations = yaml.load(f)['metadata']['annotations']
            prometheus_port_key = 'prometheus.io/port'
            prometheus_scrape_key = 'prometheus.io/scrape'
            return prometheus_port_key in annotations and prometheus_scrape_key in annotations

    def test_should_return_one_as_default_scale(self):
        assert AppExplorer(ConnectorStub()).get_deployment_scale("not_existing_service") == 1

    def test_should_return_desired_default_scale(self):
        assert AppExplorer(ConnectorStub()).get_deployment_scale("not_existing_service", 10) == 10


class TestCpuCalculator(object):
    pass

    @raises(CpuLevelNotValid)
    def test_should_fail_when_no_cpu_level(self):
        CpuCalculator(None).calculate()

    @raises(CpuLevelNotValid)
    def test_should_fail_when_cpu_level_invalid(self):
        CpuCalculator('notFound').calculate()

    def test_should_calculate_cpu(self):
        calculator = CpuCalculator('medium')
        assert calculator.calculate() == calculator.cpu_mapping['medium']

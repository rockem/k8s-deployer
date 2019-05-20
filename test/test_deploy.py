from nose.tools import raises
from os import environ

from deployer.deploy import DeployError, ImageDeployer, ColorDecider, DeployPropsCreator
from deployer.recipe import RecipeBuilder, Recipe


class HealthCheckerStub(object):
    def __init__(self, healthy):
        self.healthy = healthy
        self.health_called = False

    def health_check(self):
        self.health_called = True
        return self.healthy


class K8sDeployerStub(object):
    def __init__(self, connector):
        self.connector = connector
        self.deploy_called = False

    def deploy(self, target):
        self.deploy_called = True


class ConnectorStub(object):
    def __init__(self, healthy=True):
        self.healthy = healthy
        self.applied_descriptors = {}
        self.applied_scale = {}
        self.activated_deployments = []
        self.applied_services = {}
        self.applied_service_accounts = []
        self.applied_deployments = {}
        self.applied_autoscale = False
        self.applied_ingress = False

    def apply_service(self, desc):
        self.applied_descriptors['service'] = desc
        self.applied_services[desc['serviceName']] = desc

    def apply_ingress(self, desc):
        self.applied_ingress = True

    def apply_service_account(self, desc):
        self.applied_service_accounts.append(desc)

    def apply_deployment(self, desc):
        self.applied_descriptors['deployment'] = desc
        self.applied_deployments[desc['name']] = desc

    def describe_pod(self, name):
        return "Name: %s" % name

    def apply_autoscale(self, properties):
        self.applied_autoscale = True

    def scale_deployment(self, deployment_name, scale):
        self.applied_scale[deployment_name] = scale
        if deployment_name in self.applied_deployments:
            self.applied_deployments[deployment_name]['scale'] = scale

    def check_pods_health(self, pod_name, container_name):
        return 'UP' if self.healthy else 'DOWN'

    def describe_service(self, service_name):
        if service_name in self.applied_services:
            service = self.applied_services[service_name]
            return {'spec': {'selector': {'color': service['serviceColor'],
                                          'name': service['name']}}}
        else:
            return {}

    def describe_deployment(self, deployment_name):
        if deployment_name in self.applied_deployments:
            deployment = self.applied_deployments[deployment_name]
            return {'spec': {'replicas': deployment['scale']}}

        else:
            return {}

    def activate(self, deployment):
        self.activated_deployments.append(deployment)


class TestImageDeployer(object):
    DOMAIN = 'heed'
    SICK_IMAGE_NAME = 'kuku'

    @raises(DeployError)
    def test_should_fail_given_sick_service(self):
        self.__deploy({'image_name': ('%s:123' % self.SICK_IMAGE_NAME)}, ConnectorStub(False))

    def test_should_force_deploy(self):
        self.__deploy({'image_name': ('%s:123' % self.SICK_IMAGE_NAME)}, ConnectorStub(False), force='--force')

    def test_should_scale_deployment_given_sick_service(self):
        connector = ConnectorStub(False)
        try:
            self.__deploy({'image_name': ('%s:123' % self.SICK_IMAGE_NAME)}, connector)
        except:
            pass
        color = connector.applied_descriptors['deployment']['serviceColor']
        assert connector.applied_scale[self.SICK_IMAGE_NAME + '-' + ColorDecider().invert_color(color)] == 0

    def __deploy(self, properties, connector, force=''):
        args = {"target" : 'test_target', "domain": self.DOMAIN, "deploy_timeout": 1, "force": force, "autoscale_min_pods": 1, "autoscale_max_pods": 1}
        deployer = ImageDeployer(args, connector, RecipeBuilder().ingredients(
            properties).build())
        deployer.deploy()

    def test_should_update_service_color_given_colorless_service(self):
        connector = ConnectorStub(True)
        self.__deploy({'image_name': 'no_color:123'}, connector)
        assert connector.applied_descriptors['service']['serviceColor'] == 'green'
        assert connector.applied_descriptors['deployment']['serviceColor'] == 'green'

    def test_should_not_autoscale_when_autoscale_set_to_false(self):
        connector = ConnectorStub(True)
        self.__deploy({'image_name': 'no_color:123',
                'autoscale': {'enabled': False}}, connector)
        assert not connector.applied_autoscale

    def test_should_autoscale(self):
        connector = ConnectorStub(True)
        self.__deploy({'image_name': 'no_color:123',
                       'autoscale': {'enabled': True}}, connector)
        assert connector.applied_autoscale == True

    def test_should_apply_ingress(self):
        connector = ConnectorStub(True)
        environ["TARGET_ENV"] = 'int'
        self.__deploy({'image_name': 'no_color:123',
                       'ingress': {'enabled': True}}, connector)

        assert connector.applied_ingress

    def test_should_not_apply_ingress_when_not_needed(self):
        connector = ConnectorStub(True)
        self.__deploy({'image_name': 'no_color:123',
                       'ingress': {'enabled': False}}, connector)

        assert not connector.applied_ingress

    def test_should_update_service_domain(self):
        connector = ConnectorStub(True)
        self.__deploy({'image_name': 'image:123'}, connector)
        assert connector.applied_descriptors['service']['domain'] == self.DOMAIN

    def test_skip_validation_and_deploy_when_not_exposed(self):
        connector = ConnectorStub(False)
        self.__deploy({'image_name': 'not_exposed:123', 'expose': False}, connector)
        assert connector.applied_descriptors.has_key('service') is False
        assert connector.applied_descriptors.has_key('deployment') is True

    def test_delegate_ports_details(self):
        ports = ['50:5000']
        connector = ConnectorStub(True)
        self.__deploy({'image_name': 'ported:123', 'ports': ports}, connector)
        assert connector.applied_descriptors['service']['ports'] == ports
        assert connector.applied_descriptors['deployment']['ports'] == ports

    def test_delegate_service_type(self):
        connector = ConnectorStub(True)
        self.__deploy({'image_name': 'image:123', 'service_type': 'some_type'}, connector)
        assert connector.applied_descriptors['service']['serviceType'] == 'some_type'

    def test_scale_down_background_deployment(self):
        connector = ConnectorStub(True)
        self.__deploy({'image_name': 'image:123', 'service_type': 'some_type'}, connector)
        color = connector.applied_descriptors['deployment']['serviceColor']
        assert connector.applied_scale['image-' + ColorDecider().invert_color(color)] == 0

    def test_scale_perseverance(self):
        connector = ConnectorStub(True)
        self.__deploy({'image_name': 'magnificent:123', 'service_type': 'some_type'}, connector)
        connector.scale_deployment(connector.applied_descriptors['service']['name'], 2)
        self.__deploy({'image_name': 'magnificent:456', 'service_type': 'some_type'}, connector)
        deployment = connector.describe_deployment(connector.applied_descriptors['service']['name'])
        assert deployment['spec']['replicas'] == 2

    def test_called_applied_service_account(self):
        connector = ConnectorStub(True)
        self.__deploy({'image_name': 'magnificent:123', 'service_type': 'some_type'}, connector)
        assert len(connector.applied_service_accounts) > 0


class TestDeployPropsCreator(object):

    def test_should_add_ingress_props(self):
        environ["TARGET_ENV"] = 'int'
        connector = ConnectorStub(True)
        recipe = Recipe.builder().ingredients({'ingress': {'enabled': True}, 'image_name': 'my-service:1.1'}).build()
        props = self.create_props(connector, recipe)
        assert props["ingressInfo"] == {"enabled": True, "host": "int-my-service.heed.io"}

    def create_props(self, connector, recipe):
        return DeployPropsCreator(recipe,
                                  {"domain": "heed.io", "force": False, "target": "int", "autoscale_min_pods": 1,
                                   "autoscale_max_pods": 2}, connector).create()

    def test_should_not_add_ingress_info_when_ingress_not_enabled(self):
        connector = ConnectorStub(True)
        recipe = Recipe.builder().ingredients({'ingress': {'enabled': False}, 'image_name': 'my-service:1.1'}).build()
        props = self.create_props(connector, recipe)
        assert props["ingressInfo"] == {"enabled": False}

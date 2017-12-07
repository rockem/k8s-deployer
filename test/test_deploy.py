from nose.tools import raises

from deployer.deploy import DeployError, ImageDeployer, ColorDecider
from deployer.recipe import RecipeBuilder


class HealthCheckerStub(object):
    def __init__(self, healthy):
        self.healthy = healthy
        self.health_called = False

    def health_check(self, pod_name):
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

    def apply_service(self, desc):
        self.applied_descriptors['service'] = desc

    def apply_deployment(self, desc):
        self.applied_descriptors['deployment'] = desc

    def describe_pod(self, name):
        return "Name: %s" % name

    def scale_deployment(self, deployment_name, scale):
        self.applied_scale[deployment_name] = scale

    def check_pods_health(self, pod_name, container_name):
        return 'UP' if self.healthy else 'DOWN'

    def get_service_as_json(self, service_name):
        if service_name == 'no_color':
            return str('{"spec": {"selector": {"no_color": "no"}}}')
        else:
            return str('{"spec": {"selector": {"color": "green"}}}')


class TestImageDeployer(object):
    DOMAIN = 'heed'

    @raises(DeployError)
    def test_should_fail_given_sick_service(self):
        self.__deploy(False, {'image_name': 'kuku:123'})

    def __deploy(self, healthy, properties):
        self.connector = ConnectorStub(healthy)
        deployer = ImageDeployer('test_target', self.DOMAIN, self.connector, RecipeBuilder().ingredients(
            properties).build(), 1)
        deployer.deploy()

    def test_should_update_service_color_given_colorless_service(self):
        self.__deploy(True, {'image_name': 'no_color:123'})
        assert self.connector.applied_descriptors['service']['serviceColor'] == 'green'
        assert self.connector.applied_descriptors['deployment']['serviceColor'] == 'green'

    def test_should_update_service_domain(self):
        self.__deploy(True, {'image_name': 'image:123'})
        assert self.connector.applied_descriptors['service']['domain'] == self.DOMAIN

    def test_skip_validation_and_deploy_when_not_exposed(self):
        self.__deploy(False, {'image_name': 'not_exposed:123', 'expose': False})
        assert self.connector.applied_descriptors.has_key('service') is False
        assert self.connector.applied_descriptors.has_key('deployment') is True

    def test_delegate_ports_details(self):
        ports = ['50:5000']
        self.__deploy(True, {'image_name': 'ported:123', 'ports': ports})
        assert self.connector.applied_descriptors['service']['ports'] == ports
        assert self.connector.applied_descriptors['deployment']['ports'] == ports

    def test_delegate_service_type(self):
        self.__deploy(True, {'image_name': 'image:123', 'service_type': 'some_type'})
        assert self.connector.applied_descriptors['service']['serviceType'] == 'some_type'

    def test_scale_down_background_deployment(self):
        self.__deploy(True, {'image_name': 'image:123', 'service_type': 'some_type'})
        color = self.connector.applied_descriptors['deployment']['serviceColor']
        assert self.connector.applied_scale['image-' + ColorDecider().invert_color(color)] == 0

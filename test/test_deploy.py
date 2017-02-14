from nose.tools import raises

from deployer.deploy import DeployError, ImageDeployer


class RecipeStub(object):

    def __init__(self, path):
        self.path = path

    def expose(self):
        if self.path == 'exposed':
            return True
        else:
            return False

class HealthCheckerStub(object):
    def __init__(self, healthy):
        self.healthy = healthy
        self.health_called = False

    def health_check(self, pod_name):
        self.health_called = True
        return self.healthy

class DeployRunnerStub(object):

    def deploy(self, config, elements):
        pass

class ConnectorStub(object):
    def __init__(self, namespace):
        self.namespace = namespace

    def get_service_as_json(self, service_name):
        if service_name == 'no_color':
            return str('{"spec": {"selector": {"no_color": "no"}}}')
        else:
            return str('{"spec": {"selector": {"color": "green"}}}')

class TestImageDeployer():

    @raises(DeployError)
    def test_should_fail_given_sick_service(self):
        self.deploy_image('sick_image:0.1', False, 'exposed')

    def deploy_image(self, image_name, is_check_health, recipe):
        deployer = ImageDeployer(image_name, 'test_target', ConnectorStub('test_namespace'), RecipeStub(recipe))
        deployer.health_checker = HealthCheckerStub(is_check_health)
        deployer.deploy_runner = DeployRunnerStub()
        deployer.deploy()
        return deployer

    def test_should_update_service_color_given_colorless_service(self):
        assert self.deploy_image('no_color:0.1', True, 'exposed').configuration.get('serviceColor') == 'green'

    def test_skip_validation_and_deploy_given_route53_kubernetes(self):
        deployer = self.deploy_image('not_exposed:0.1', False, 'not_exposed')
        assert deployer.health_checker.health_called is False
        assert deployer.configuration.get('name') == 'not_exposed'
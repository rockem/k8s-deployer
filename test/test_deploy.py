from nose.tools import raises

from deployer.deploy import DeployError, ImageDeployer


class HealthCheckerStub(object):
    def __init__(self, healthy):
        self.healthy = healthy

    def health_check(self, pod_name):
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
        deployer = ImageDeployer('sick_image:0.1', 'test_target', ConnectorStub('test_namespace'))
        deployer.health_checker = HealthCheckerStub(False)
        deployer.deploy_runner = DeployRunnerStub()
        deployer.deploy()

    def test_should_update_service_color_given_colorless_service(self):
        deployer = ImageDeployer('no_color:0.1', 'test_target', ConnectorStub('test_namespace'))
        deployer.health_checker = HealthCheckerStub(True)
        deployer.deploy_runner = DeployRunnerStub()
        deployer.deploy()
        assert deployer.configuration.get('serviceColor') == 'green'

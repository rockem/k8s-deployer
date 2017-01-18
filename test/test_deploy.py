from nose.tools import raises

from deployer.deploy import DeployError, ImageDeployer


class HealthCheckerStub(object):
    def __init__(self, healthy):
        self.healthy = healthy

    def health_check(self):
        return self.healthy

class DeployRunnerStub(object):

    def deploy(self, config, elements):
        pass

class TestImageDeployer():

    @raises(DeployError)
    def test_should_fail_given_sick_service(self):
        deployer = ImageDeployer('sick_image:0.1', 'test_target')
        deployer.health_checker = HealthCheckerStub(False)
        deployer.deploy_runner = DeployRunnerStub()
        deployer.deploy()

from nose.tools import raises

from deployer.deploy import DeployError, ImageDeployer
from deployer.file import YamlReader
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
        self.connector=connector
        self.deploy_called = False

    def deploy(self,target):
        self.deploy_called = True


class ConnectorStub(object):
    def __init__(self, namespace):
        self.namespace = namespace

    def get_service_as_json(self, service_name):
        if service_name == 'no_color':
            return str('{"spec": {"selector": {"no_color": "no"}}}')
        else:
            return str('{"spec": {"selector": {"color": "green"}}}')



class TestImageDeployer(object):
    @raises(DeployError)
    def test_should_fail_given_sick_service(self):
        self.__deploy_image('sick_image:0.1', False,{'expose':'exposed',"logging":"none"})

    def __deploy_image(self, image_name, is_check_health, recipe):
        connector_stub = ConnectorStub('test_namespace')
        deployer = ImageDeployer('test_target', connector_stub, RecipeBuilder().ingredients(
            {'image_name': image_name, 'expose': recipe['expose'] is 'exposed',"logging":recipe["logging"]}).build(), 1)
        deployer.health_checker = HealthCheckerStub(is_check_health)
        deployer.k8s_deployer = K8sDeployerStub(connector_stub)
        deployer.deploy()
        return deployer

    def test_should_not_append_logging(self):
         self.__deploy_image('no_color:0.1', True, {'expose':'exposed','logging':'none'})
         assert cmp(YamlReader("./test/out/deployment.yml").read(),YamlReader("./test/orig/deployment.yml").read()) == 0


    def test_should_update_service_color_given_colorless_service(self):
        assert self.__deploy_image('no_color:0.1', True, {'expose':'exposed','logging':'none'}).configuration.get('serviceColor') == 'green'

    def test_skip_validation_and_deploy_given_route53_kubernetes(self):
        deployer = self.__deploy_image('not_exposed:0.1', False, {'expose':'not_exposed','logging':'none'})
        assert deployer.health_checker.health_called is False

        assert deployer.configuration.get('name') == 'not_exposed'

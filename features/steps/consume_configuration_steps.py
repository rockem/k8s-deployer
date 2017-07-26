import requests
from behave import then, given
from behave import use_step_matcher

from deployer.log import DeployerLogger
from features.support.context import Context
from features.support.k8s import K8sDriver

logger = DeployerLogger(__name__).getLogger()

use_step_matcher("re")


@given("config \"(.*)\" was uploaded")
def upload_config(context, config_name):
    K8sDriver(Context(context).default_namespace(), context.minikube).upload_config(config_name)


@then("the service should get the new configuration")
def verify_config_was_overriden(context):
    svc_host = K8sDriver(Context(context).default_namespace(), context.minikube).get_service_domain_for(
        Context(context).last_deployed_app())
    assert __get_greeting_of(svc_host) == 'Hello overridden world'


def __get_greeting_of(svc_host):
    url = 'http://%s/greeting' % svc_host
    return requests.get(url).text

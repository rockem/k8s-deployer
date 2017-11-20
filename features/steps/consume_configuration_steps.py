from behave import then, given
from behave import use_step_matcher

from deployer.log import DeployerLogger
from features.support.context import Context
from features.support.http import http_get, url_for
from features.support.k8s import K8sDriver

logger = DeployerLogger(__name__).getLogger()

use_step_matcher("re")


@given("config \"(.*)\" was uploaded")
def upload_config(context, config_name):
    K8sDriver(Context(context).default_namespace(), context.minikube).upload_config(config_name)


@then("the service should get the new configuration")
def verify_config_was_overriden(context):
    K8sDriver(Context(context).default_namespace()).verify_get(
        '%s/greeting' % url_for(Context(context).last_deployed_app()),
        lambda output: output == 'Hello overridden world')

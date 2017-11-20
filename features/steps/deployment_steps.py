from behave import *

from features.support.context import Context
from features.support.http import url_for
from features.support.k8s import K8sDriver

use_step_matcher("re")


@then("it should be running")
def pod_running(context):
    K8sDriver(Context(context).default_namespace(), context.minikube).verify_app_is_running(
        Context(context).last_deployed_app())


@then("port 5000 is available")
def verify_port_available(context):
    K8sDriver(Context(context).default_namespace()).verify_get(
        '%s/greet' % url_for(Context(context).last_deployed_app(), 5000),
        lambda output: output == "Hello Ported")

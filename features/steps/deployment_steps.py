from behave import *

from features.support.context import Context
from features.support.k8s import K8sDriver

use_step_matcher("re")


@then("it should be running")
def pod_running(context):
    K8sDriver(Context(context).default_namespace(), context.minikube).verify_app_is_running(
        Context(context).last_deployed_app())

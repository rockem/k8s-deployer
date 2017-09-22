import requests
from behave import *
from requests.adapters import HTTPAdapter

from features.support.context import Context
from features.support.http import http_get
from features.support.k8s import K8sDriver

use_step_matcher("re")


@then("it should be running")
def pod_running(context):
    K8sDriver(Context(context).default_namespace(), context.minikube).verify_app_is_running(
        Context(context).last_deployed_app())


@then("port 5000 is available")
def step_impl(context):
    domain = K8sDriver(Context(context).default_namespace(), context.minikube).get_service_domain_for(
        Context(context).last_deployed_app(), 'tcp-5000')
    assert http_get('http://%s/greet' % domain).text == "Hello Ported"

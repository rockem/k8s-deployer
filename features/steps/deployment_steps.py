import yaml

from behave import *

from features.support.context import Context
from features.support.deploy import DeployerDriver
from features.support.http import http_get
from features.support.k8s import K8sDriver
from features.support.repository import SwaggerRepository
from random_words import RandomWords
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


@given("swagger committed")
def swagger_committed(context):
    random = RandomWords().random_word()
    last_commit = SwaggerRepository().push_swagger_with(random)
    Context(context).add_swagger_path(SwaggerRepository().get_path(last_commit))
    Context(context).add_swagger_response(random)


@when("deployed to apigateway")
def apiGateway(context):
    DeployerDriver("", Context(context).default_namespace(), context.domain, Context(context).get_swagger_path()).deploy_swagger(Context(context).get_swagger_path())

@then("apigateway should running")
def step_impl(context):
    assert yaml.load(http_get('https://y404vvoq21.execute-api.us-east-1.amazonaws.com/int/v1/random').text) ==  Context(context).get_swagger_response()
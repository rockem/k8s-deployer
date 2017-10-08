import yaml

from behave import *

from features.support.app import BusyWait
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
    SwaggerRepository().push_swagger()
    SwaggerRepository().update_swagger_with(random)
    Context(context).add_swagger_path(SwaggerRepository.SWAGGER_YML_URL)
    Context(context).add_swagger_response(random)


@when("deployed to apigateway")
def apiGateway(context):
    DeployerDriver("", Context(context).default_namespace(), context.domain, Context(context).get_swagger_path()).deploy_swagger(Context(context).get_swagger_path())

@then("apigateway should running")
def step_impl(context):
    BusyWait.execute(__validate_api_gateway_updated,Context(context).get_swagger_response())

def __validate_api_gateway_updated(response):
    assert yaml.load(http_get('https://y404vvoq21.execute-api.us-east-1.amazonaws.com/int/v1/random').text) == response

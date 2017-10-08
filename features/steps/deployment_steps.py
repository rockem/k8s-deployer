import os
import yaml

from behave import *

from features.support.app import BusyWait
from features.support.context import Context
from features.support.deploy import DeployerDriver
from features.support.http import http_get
from features.support.k8s import K8sDriver
from features.support.repository import SwaggerFileCreator
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


@given("swagger generated with random response")
def swagger_committed(context):
    random = RandomWords().random_word()
    SwaggerFileCreator().create_yml() #TODO: 1 function
    SwaggerFileCreator().update_yml_with(random)
    Context(context).add_swagger_response(random)


@when("deploying swagger")
def apiGateway(context):
    DeployerDriver("", Context(context).default_namespace(), context.domain, SwaggerFileCreator.SWAGGER_YML_URL)\
        .deploy_swagger(SwaggerFileCreator.SWAGGER_YML_URL)


@then("swagger uploaded correctly to api gw")
def step_impl(context):
    BusyWait.execute(__validate_api_gateway_updated, Context(context).get_swagger_response())


def __validate_api_gateway_updated(response):
    assert yaml.load(http_get("https://"+os.environ['REST_API_ID']+".execute-api.us-east-1.amazonaws.com/int/v1/random").text) == response

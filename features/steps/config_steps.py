import os
import yaml
from behave import *
import requests
from random_words import RandomWords

from features.support.app import BusyWait
from features.support.context import Context
from features.support.deploy import DeployerDriver
from features.support.http import http_get
from features.support.k8s import K8sDriver
from features.support.repository import ConfigRepository, LocalConfig, SwaggerFileCreator, LoggingRepository

use_step_matcher("re")


@given("config \"(.*)\" was pushed to git")
def push_config(context, config_name):
    ConfigRepository().push_config(config_name)


@given("job \"(.*)\" was pushed to git")
def push_config(context, job_name):
    ConfigRepository().push_job(job_name)


@given('namespace "(.+)" doesn\'t exists')
def clear_namespace(context, namespace):
    K8sDriver(namespace, context.minikube).delete_namespace()
    Context(context).add_namespace_to_delete(namespace)


@when("configuring(?: \"(.+)\")?")
def executing(context, namespace=None):
    DeployerDriver(ConfigRepository.GIT_REPO_URL,
                   Context(context).default_namespace() if namespace is None else namespace,context.domain).configure()


@then("config \"(.*)\" uploaded(?: to \"(.+)\" namespace)?")
def validate_config_uploaded(context, config_name, namespace=None):
    ns = Context(context).default_namespace() if namespace is None else namespace
    K8sDriver(ns, context.minikube).verify_config_is(LocalConfig(config_name).content())


@then("the job for \"(.*):(.*)\" service was invoked")
def jobs_were_invoked_on_service(context, service, version):
    domain = K8sDriver(Context(context).default_namespace(), context.minikube).get_service_domain_for(
        Context(context).get_app_for(service, version))
    BusyWait.execute(_validate_job_was_invoked, domain)


def _validate_job_was_invoked(domain):
    assert http_get('http://%s/verify' % domain).status_code == 200


@given("swagger generated with random response")
def swagger_committed(context):
    random = RandomWords().random_word()
    SwaggerFileCreator().create_yml_with(random)
    Context(context).add_swagger_response(random)


@when("deploying swagger")
def deploy_swagger(context):
    DeployerDriver(LoggingRepository.GIT_REPO_URL, Context(context).default_namespace(), context.domain,
                   SwaggerFileCreator.SWAGGER_YML_URL) \
        .deploy_swagger(SwaggerFileCreator.SWAGGER_YML_URL)


@then("uploaded to api gw")
def verify_swagger_uploaded(context):
    BusyWait.execute(__validate_api_gateway_updated, Context(context).get_swagger_response())


@then("swagger logged in git")
def verify_swagger_uploaded(context):
    LoggingRepository().verify_swagger_is_logged()


def __validate_api_gateway_updated(response):
    assert http_get( "https://" + os.environ['REST_API_ID'] + ".execute-api.us-east-1.amazonaws.com/int/v1/random").text == response



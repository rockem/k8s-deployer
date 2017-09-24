import requests
import time
from behave import *
from flask import json

from features.support.app import BusyWait
from features.support.context import Context
from features.support.deploy import DeployerDriver
from features.support.k8s import K8sDriver
from features.support.repository import RecipeRepository

use_step_matcher("re")


@when("deploy \"(.*):(.*)\" service(?: should (.*))?")
def deploy_healthy_service(context, name, version, status):
    __deploy_service(context, name, version, status)


@given("\"(.*):(.*)\" service was deployed successfully")
def deploy_service_successfully(context, name, version):
    __deploy_service(context, name, version, 'success')


def __deploy_service(context, name, version, status):
    app = Context(context).get_app_for(name, version)
    DeployerDriver(RecipeRepository.GIT_REPO_URL, Context(context).default_namespace()).deploy(app, status == 'fail')
    Context(context).set_last_deployed_app(app)


@then("\"(.*)\" service is serving")
def service_is_serving(context, service_name):
    K8sDriver(Context(context).default_namespace(), context.minikube).get_service_domain_for(
        context.config.userdata['apps'][service_name])


@then("service \"(.*)\" updated to version (.*)")
def service_updated(context, name, version):
    domain = K8sDriver(Context(context).default_namespace(), context.minikube).get_service_domain_for(
        Context(context).get_app_for(name, version))
    BusyWait.execute(__validate_version_updated, domain, version)

def __validate_version_updated(domain, version):
    result = requests.get('http://%s/version' % domain)
    assert json.loads(result.text)['version'] == str(version), 'Healthy service not serving anymore'

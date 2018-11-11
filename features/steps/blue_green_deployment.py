from behave import *
from flask import json

from features.support.context import Context
from features.support.deploy import DeployerDriver
from features.support.http import url_for
from features.support.k8s import K8sDriver
from features.support.repository import LoggingRepository

use_step_matcher("re")


@when("(?:(.*) )?deploy \"(.*):(.*)\" service(?: should (.*))?")
def deploy_healthy_service(context, force, name, version, status):
    __deploy_service(context, name, version, status, force)

def __deploy_service(context, name, version, status, force):
    app = Context(context).get_app_for(name, version)
    DeployerDriver(LoggingRepository.GIT_REPO_URL, Context(context).default_namespace(), context.domain, Context(context).get_mongo_uri(), force == 'force').deploy(app, status == 'fail')
    Context(context).set_last_deployed_app(app)

@then("all is good")
def all_is_good(context):
    print("all is good")


@then("\"(.*)\" service is serving")
def service_is_serving(context, service_name):
    K8sDriver(Context(context).default_namespace()).wait_to_serve(
        context.config.userdata['apps'][service_name])


@then("service \"(.*)\" updated to version (.*)")
def service_updated(context, name, version):
    K8sDriver(Context(context).default_namespace()).verify_get(
        '%s/version' % url_for(Context(context).get_app_for(name, version)),
        lambda response: json.loads(response)['version'] == version)


@when("rollback \"(.*):(.*)\" service")
def rollback_current_service(context, name, version):
    DeployerDriver(LoggingRepository.GIT_REPO_URL,
                   Context(context).default_namespace(), context.domain, Context(context).get_mongo_uri()).rollback(Context(context).get_app_for(name, version).service_name())



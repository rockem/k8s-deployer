import requests
import time

from behave import *
from flask import json

from features.steps.support import TARGET_ENV_AND_NAMESPACE, GIT_REPO_URL, NAMESPACE
from features.support.context import Context
from features.support.deploy import DeployerDriver
from features.support.docker import AppImage
from features.support.k8s import K8sDriver

use_step_matcher("re")


@when("deploy \"(.*):(.*)\" service(?: should (.*))?")
def deploy_healthy_service(context, name, version, status):
    app = Context(context).get_app_for(name, version)
    DeployerDriver(GIT_REPO_URL, TARGET_ENV_AND_NAMESPACE).deploy(app, status == 'fail')
    Context(context).set_last_deployed_app(app)


@then("\"(.*)\" service is serving")
def service_is_serving(context, service_name):
    K8sDriver(NAMESPACE, context.minikube).get_service_domain_for(
        context.config.userdata['apps'][service_name])


@then("service \"(.*)\" updated to version (.*)")
def service_updated(context, name, version):
    domain = K8sDriver(NAMESPACE, context.minikube).get_service_domain_for(
        Context(context).get_app_for(name, version))
    __busy_wait(__validate_version_updated,domain, version)

def __busy_wait(run_func, *args):
    result = False
    for _ in range(20):
        try:
            if run_func(*args):
                result = True
                break
        except Exception:
            pass
        time.sleep(1)

    return result
def __validate_version_updated(domain, version):
    result = requests.get('http://%s/version' % domain)
    assert json.loads(result.text)['version'] == str(version), 'Healthy service not serving anymore'

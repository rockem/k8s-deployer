from behave import *
import requests

from features.support.app import BusyWait
from features.support.context import Context
from features.support.deploy import DeployerDriver
from features.support.http import http_get
from features.support.k8s import K8sDriver
from features.support.repository import ConfigRepository, LocalConfig

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
                   Context(context).default_namespace() if namespace is None else namespace, context.domain,
                   Context(context).get_swagger_path()).configure()


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

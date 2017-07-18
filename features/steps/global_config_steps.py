from behave import *

from features.environment import GIT_REPO_URL
from features.support.context import Context
from features.support.deploy import DeployerDriver
from features.support.k8s import K8sDriver
from features.support.repository import ConfigRepository, LocalConfig

use_step_matcher("re")


@given("config \"(.*)\" was pushed to git")
def push_config(context, config_name):
    ConfigRepository().push_config(config_name)

@given('namespace "(.+)" doesn\'t exists')
def clear_namespace(context, namespace):
    K8sDriver(namespace, context.minikube).delete_namespace()
    Context(context).add_namespace_to_delete(namespace)

@when("configuring(?: \"(.+)\")?")
def executing(context, namespace = None):
    DeployerDriver(GIT_REPO_URL, Context(context).default_namespace() if namespace == None else namespace).configure()

@then("config \"(.*)\" uploaded(?: to \"(.+)\" namespace)?")
def validate_config_uploaded(context, config_name, namespace=None):
    ns = Context(context).default_namespace() if namespace is None else namespace
    K8sDriver(ns, context.minikube).verify_config_is(LocalConfig(config_name).content())

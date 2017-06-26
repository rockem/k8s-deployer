from behave import *

from features.steps.support import GIT_REPO_URL, TARGET_ENV, get_target_environment
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
def executing(context, namespace=None):
    DeployerDriver(GIT_REPO_URL, __get_target(context, namespace)).configure()


def __get_target(context, namespace):
    return get_target_environment(context) if namespace is None else "%s:%s" % (TARGET_ENV, namespace)


@then("config \"(.*)\" uploaded(?: to \"(.+)\" namespace)?")
def validate_config_uploaded(context, config_name, namespace=None):
    ns = Context(context).default_namespace() if namespace is None else namespace
    K8sDriver(ns, context.minikube).verify_config_is(LocalConfig(config_name).content())


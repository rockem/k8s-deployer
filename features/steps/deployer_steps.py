import os
import subprocess

import re

import time
from behave import *

from deployer.log import DeployerLogger
from features.steps.support import  JAVA_SERVICE_NAME, GIT_REPO_URL, \
    TARGET_ENV, get_target_environment
from features.support.app import AppDriver
from features.support.context import Context
from features.support.k8s import K8sDriver

use_step_matcher("re")
CONFIG_MAP = 'global-config'

@when('deploying to namespace(?: \"(.+)\")?')
def deploy(context, namespace):
    target = get_target_environment(context) if namespace is None else "%s:%s" % (TARGET_ENV, namespace)
    subprocess.check_output("python deployer/deployer.py deploy --image_name %s --target %s --git_repository %s" %
                            ('%sdeployer-test-java:1.0' % context.aws_uri, target, GIT_REPO_URL), shell=True)


@then("service is deployed(?: in \"(.+)\")?")
def is_deployed(context, namespace):
    namespace =  Context(context).default_namespace() if namespace is None else namespace
    output = os.popen("kubectl get svc %s --namespace=%s" % (JAVA_SERVICE_NAME, namespace)).read()
    assert JAVA_SERVICE_NAME in output


@then("it should be running")
def pod_running(context):
    K8sDriver( Context(context).default_namespace(), context.minikube).verify_app_is_running(Context(context).last_deployed_app())
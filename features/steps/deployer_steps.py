import os
import subprocess

import re

import time
from behave import *

from deployer.log import DeployerLogger
from features.steps.support import NAMESPACE, JAVA_SERVICE_NAME, GIT_REPO_URL, \
    TARGET_ENV, TARGET_ENV_AND_NAMESPACE
from features.support.app import AppDriver
from features.support.context import Context
from features.support.k8s import K8sDriver

use_step_matcher("re")
CONFIG_MAP = 'global-config'

logger = DeployerLogger(__name__).getLogger()


@when('deploying to namespace(?: \"(.+)\")?')
def deploy(context, namespace):
    logger.debug('deploy java service to k8s')
    target = TARGET_ENV_AND_NAMESPACE if namespace is None else "%s:%s" % (TARGET_ENV, namespace)
    subprocess.check_output("python deployer/deployer.py deploy --image_name %s --target %s --git_repository %s" %
                            ('%sdeployer-test-java:1.0' % context.aws_uri, target, GIT_REPO_URL), shell=True)


@then("service is deployed(?: in \"(.+)\")?")
def is_deployed(context, namespace):
    K8sDriver(NAMESPACE, context.minikube).

    logger.info('service:%s, namespace:%s' % (JAVA_SERVICE_NAME, NAMESPACE))
    namespace = NAMESPACE if namespace is None else namespace
    output = os.popen("kubectl get svc %s --namespace=%s" % (JAVA_SERVICE_NAME, namespace)).read()
    assert JAVA_SERVICE_NAME in output


@then("it should be running")
def pod_running(context):
    K8sDriver(NAMESPACE, context.minikube).verify_app_is_running(Context(context).last_deployed_app())
    # assert __busy_wait(__pod_running, context.currentImageName)


def __busy_wait(run_func, *args):
    result = False
    for _ in range(20):  # TODO - should be 120
        try:
            if run_func(*args):
                result = True
                break
        except Exception:
            pass
        time.sleep(1)

    return result


def __pod_running(image_name):
    pod_name = __grab_pod_name(image_name)
    match = re.search(r"Status:\s(.*)", __describe_pod(pod_name))
    if match:
        return match.group(1).strip() == 'Running'
    else:
        raise Exception('service %s has no pod!' % pod_name)


def __describe_pod(pod_name):
    return __run("kubectl --namespace %s describe pods %s" % (NAMESPACE, pod_name))


def __grab_pod_name(pod_name):
    output = __run("kubectl --namespace %s get pods" % (NAMESPACE))
    list = output.split()
    for item in list:
        if item.startswith(pod_name):
            return item


def __run(command):
    return subprocess.check_output(command, shell=True)

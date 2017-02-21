import os
import subprocess

import re
from behave import *

from deployer.log import DeployerLogger
from features.steps.blue_green_deployment import AUTOGEN_SERVICE_NAME
from features.steps.support import NAMESPACE, JAVA_SERVICE_IMAGE_NAME, JAVA_SERVICE_NAME, GIT_REPO_URL, \
    TARGET_ENV, TARGET_ENV_AND_NAMESPACE

use_step_matcher("re")
CONFIG_MAP = 'global-config'

logger = DeployerLogger(__name__).getLogger()


@when('deploying to namespace(?: \"(.+)\")?')
def deploy(context, namespace):
    logger.debug('deploy java service to k8s')
    target = TARGET_ENV_AND_NAMESPACE if namespace is None else "%s:%s" % (TARGET_ENV, namespace)
    subprocess.check_output("python deployer/deployer.py deploy --image_name %s --target %s --git_repository %s" %
                            (JAVA_SERVICE_IMAGE_NAME, target, GIT_REPO_URL), shell=True)


@then("service is deployed(?: in \"(.+)\")?")
def is_deployed(context, namespace):
    logger.info('service:%s, namespace:%s' % (JAVA_SERVICE_NAME, NAMESPACE))
    namespace = NAMESPACE if namespace is None else namespace
    output = os.popen("kubectl get svc %s --namespace=%s" % (JAVA_SERVICE_NAME, namespace)).read()
    assert JAVA_SERVICE_NAME in output


@then("pod is up and running")
def pod_running(context):
    assert __pod_status(AUTOGEN_SERVICE_NAME) == 'Running'


def __pod_status(pod_name):
    match = re.search(r"Status:\s(.*)", __describe_pod())
    if match:
        return match.group(1).strip()
    else:
        raise Exception('service %s has no pod!' % pod_name)


def __describe_pod():
    return __run("kubectl --namespace %s get pods" % (NAMESPACE))


def __run(command):
    return subprocess.check_output(command, shell=True)

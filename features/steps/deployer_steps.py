import os

import subprocess
from behave import *
from deployer.log import DeployerLogger
from features.steps.support import NAMESPACE, JAVA_SERVICE_IMAGE_NAME, JAVA_SERVICE_NAME ,GIT_REPO_URL, \
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


@then("service should be deployed(?: in \"(.+)\")?")
def should_be_deployed(context, namespace):
    logger.info('service:%s, namespace:%s' % (JAVA_SERVICE_NAME, NAMESPACE))
    namespace = NAMESPACE if namespace is None else namespace
    context.config.userdata["namespace"] = namespace
    output = os.popen("kubectl get svc %s --namespace=%s" % (JAVA_SERVICE_NAME, namespace)).read()
    assert JAVA_SERVICE_NAME in output


@given('namespace "(.+)" doesn\'t exists')
def delete_namespace(context, namespace=None):
    n = context.config.userdata["namespace"] if namespace is None else namespace
    os.system("kubectl delete namespace %s" % n)
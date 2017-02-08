import os

import subprocess
from behave import *
from deployer.log import DeployerLogger
from features.steps.blue_green_deployment import HEALTHY_NAME
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


@then("service (.+) is deployed(?: in \"(.+)\")?")
def is_deployed(context,service ,namespace):
    service_dic = {'health': HEALTHY_NAME, 'java': JAVA_SERVICE_NAME }
    name = service_dic[service]
    logger.info('service:%s, namespace:%s' % (name, NAMESPACE))
    namespace = NAMESPACE if namespace is None else namespace
    output = os.popen("kubectl get svc %s --namespace=%s" % (name, namespace)).read()
    assert name in output
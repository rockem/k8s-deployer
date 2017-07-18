import os
import subprocess
from behave import *

from features.environment import JAVA_SERVICE_NAME, TARGET_ENV,  GIT_REPO_URL

from features.support.context import Context
from features.support.k8s import K8sDriver


use_step_matcher("re")

@when('deploying to namespace(?: \"(.+)\")?')
def deploy(context, namespace):
    target = context.default_namespace() if namespace is None else "%s:%s" % (TARGET_ENV, namespace)
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


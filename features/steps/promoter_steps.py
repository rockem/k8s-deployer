import os

from behave import given, then, when
from deployer.log import DeployerLogger
from deployer.services import ServiceVersionWriter, ServiceVersionReader
from features.steps.support import JAVA_SERVICE_IMAGE_NAME, JAVA_SERVICE_NAME, GIT_REPO, TARGET_ENV, \
    TARGET_ENV_AND_NAMESPACE

logger = DeployerLogger(__name__).getLogger()


@given("service is defined in source environment")
def write_service_to_int_git(context):
    ServiceVersionWriter(GIT_REPO).write('kuku', JAVA_SERVICE_NAME, JAVA_SERVICE_IMAGE_NAME)


@when("promoting to production")
def promote(context):
    assert os.system("python deployer/deployer.py promote --source kuku --target %s "
                     "--git_repository %s" % (TARGET_ENV_AND_NAMESPACE, GIT_REPO)) == 0


@then("service should be logged in git")
def check_promoted_service_in_git(context):
    assert ServiceVersionReader(GIT_REPO).read(TARGET_ENV)[0] == JAVA_SERVICE_IMAGE_NAME


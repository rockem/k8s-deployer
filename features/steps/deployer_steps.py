import os
from behave import *
from deployer.services import ServiceVersionWriter, ServiceVersionReader

use_step_matcher("re")
REPO_NAME = 'behave_repo'
GIT_REPO = "file://" + os.getcwd() + '/' + REPO_NAME
SERVICE_NAME = "deployer-stub"
IMAGE_NAME = SERVICE_NAME + ":latest"


@given("service is dockerized")
def dockerize(context):
    os.system("docker build -t %s ./features/service_stub/." % SERVICE_NAME)


@when('execute')
def execute(context):
    assert os.system(
        "python deployer/deployer.py --action deploy --image_name %s --target ct-int "
        "--git_repository %s" % (IMAGE_NAME, GIT_REPO)) == 0


@then("service should be deployed( .*)?")
def should_be_deployed(context, env):
    output = os.popen("kubectl get svc %s" % SERVICE_NAME).read()
    assert SERVICE_NAME in output


@then("service name and version is written to git")
def check_git(context):
    assert ServiceVersionReader(GIT_REPO).read('ct-int')[0] == IMAGE_NAME


@given("service is in integration")
def write_service_to_int_git(context):
    ServiceVersionWriter(GIT_REPO).write('ct-int', SERVICE_NAME, IMAGE_NAME)


@when("promoting to production")
def promote(context):
    assert os.system("python deployer/deployer.py --action promote --source ct-int --target ct-prod "
                     "--git_repository %s" % GIT_REPO) == 0


@then("the promoted service should be logged in git")
def check_promoted_service_in_git(context):
    assert ServiceVersionReader(REPO_NAME).read('ct-prod')[0] == IMAGE_NAME

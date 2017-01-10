import getpass
import os

import time
from behave import *
from deployer.services import ServiceVersionWriter, ServiceVersionReader

use_step_matcher("re")
TARGET_ENV = 'int'
REPO_NAME = 'behave_repo'
GIT_REPO = "file://" + os.getcwd() + '/' + REPO_NAME
#GIT_REPO = 'https://git.dnsk.io/media-platform/k8s-services-envs'
SERVICE_NAME = "deployer-stub-" + getpass.getuser() + "-" + str(int(time.time()))

IMAGE_NAME = SERVICE_NAME + ":latest"


@given("service is dockerized")
def dockerize(context):
    os.system("docker build -t %s ./features/service_stub/." % SERVICE_NAME)


@when('deploying')
def deploy(context):
    assert os.system(
        "python deployer/deployer.py deploy --image_name %s --target %s "
        "--git_repository %s" % (IMAGE_NAME, TARGET_ENV, GIT_REPO)) == 0


@then("service should be deployed( .*)?")
def should_be_deployed(context, env):
    output = os.popen("kubectl get svc %s" % SERVICE_NAME).read()
    assert SERVICE_NAME in output


@given("service is defined in source environment")
def write_service_to_int_git(context):
    ServiceVersionWriter(GIT_REPO).write('kuku', SERVICE_NAME, IMAGE_NAME)


@when("promoting to production")
def promote(context):
    assert os.system("python deployer/deployer.py promote --source kuku --target %s "
                     "--git_repository %s" % (TARGET_ENV, GIT_REPO)) == 0


@then("service should be logged in git")
def check_promoted_service_in_git(context):
    assert ServiceVersionReader(GIT_REPO).read(TARGET_ENV)[0] == IMAGE_NAME

@given("healthy service")
def deploy_healthy_service(context):
    print 'y6ay'

@when("deploying sick service")
def deploy_sick_service(context):
    print 'y6ay'

@then("healthy service still serving")
def healthy_service_is_serving(context):
    print 'yay'

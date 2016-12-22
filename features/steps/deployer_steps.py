import os
import subprocess

from behave import *

use_step_matcher("re")

@given("service is dockerized")
def dockerize(context):
    os.system("docker build -t hello-world-java ./features/service_stub/.")

@when("execute")
def execute(context):
    subprocess.call(["python", "deployer/deployer.py", "hello-world-java"])

@then("service should be deployed")
def deploy(context):
    service_name = "deployer-stub-service"
    output = os.popen("kubectl get svc %s" % service_name).read()
    assert service_name in output

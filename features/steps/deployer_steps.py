import os
import subprocess

from behave import *

use_step_matcher("re")

@given("service is dockerized")
def dockerize(context):
    os.system("docker build -t service_dummy_test_mode ./features/service_stub/.")

@when("execute")
def execute(context):
    subprocess.call(["python", "deployer/deployer.py", "service_dummy_test_mode", "--target=target_env"])

@then("service should be deployed")
def deploy(context):
    output = os.popen("kubectl get svc dummy-service").read()
    assert "dummy-service" in output

import os
import subprocess
from behave import *
from deployer import deployRunner
from deployer.gitclient.GitClient import GitClient

use_step_matcher("re")


@given("service is dockerized")
def dockerize(context):
    os.system("docker build -t hello-world-java ./features/service_stub/.")


@when('execute')
def execute(context):
    subprocess.call(["python", "deployer/deployer.py", "hello-world-java", "deployer-comp-test"])


@then("service should be deployed")
def deploy(context):
    service_name = "deployer-stub-service"
    output = os.popen("kubectl get svc %s" % service_name).read()
    assert service_name in output


@then("service name and version is written to git")
def check_git(context):
    git_client = GitClient()
    git_client.delete_checkout_dir(deployRunner.DeployRunner.CHECKOUT_DIRECTORY)
    git_client.get_repo(deployRunner.DeployRunner.SERVICES_ENVS_REPO,
                        deployRunner.DeployRunner.CHECKOUT_DIRECTORY)
    service_file_path = 'tmp/deployer-comp-test/services/deployer-stub.yml'
    assert os.path.isfile(service_file_path)
    with open(service_file_path, 'r') as f:
        assert f.readline() == 'version: 1.1.1'

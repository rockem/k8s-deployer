import os

from behave import *

from deployer.services import ServiceVersionWriter, ServiceVersionReader

use_step_matcher("re")
git_repo = "file://" + os.getcwd() + '/behave_repo'

@given("service is dockerized")
def dockerize(context):
    os.system("docker build -t deployer-stub ./features/service_stub/.")


@when('execute')
def execute(context):
    assert os.system(
        "python deployer/deployer.py --action deploy --image_name deployer-stub:latest --target ct-prod "
        "--git_repository %s" % git_repo) == 0
    # subprocess.call(["python", "deployer/deployer.py", "--action", "deploy", "--image_name", "deployer-stub:latest",
    #                  "--target", "prod"], shell=False)


@then("service should be deployed( .*)?")
def should_be_deployed(context, env):
    service_name = "deployer-stub"
    output = os.popen("kubectl get svc %s" % service_name).read()
    assert service_name in output


@then("service name and version is written to git")
def check_git(context):
    # git_client = GitClient()
    # git_client.delete_checkout_dir(deployRunner.DeployRunner.CHECKOUT_DIRECTORY)
    # git_client.get_repo(deployRunner.DeployRunner.SERVICES_ENVS_REPO,
    #                     deployRunner.DeployRunner.CHECKOUT_DIRECTORY)
    # service_file_path = 'tmp/prod/services/deployer-stub.yml'  # 'tmp/deployer-comp-test/services/deployer-stub.yml'
    # assert os.path.isfile(service_file_path)
    # with open(service_file_path, 'r') as f:
    #     assert f.readline() == 'image_name: deployer-stub:latest'  # hello-world-java:latest'
    assert ServiceVersionReader(git_repo).read('ct-int')[0] == 'deployer-stub:latest'


@given("service is in integration")
def write_service_to_int_git(context):
    ServiceVersionWriter(git_repo).write('ct-int', 'deployer-stub', 'deployer-stub:latest')


@when("promoting to production")
def promote(context):
    assert os.system("python deployer/deployer.py promote --source ct-int --target ct-prod "
                     "--git_repository %s" % git_repo) == 0


@then("the promoted service should be logged in git")
def check_promoted_service_in_git(context):
    assert ServiceVersionReader('behave_repo').read('ct-prod')[0] == 'deployer-stub:latest'

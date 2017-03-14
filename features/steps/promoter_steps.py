import os

import yaml
from behave import given, then, when

from deployer.file import YamlReader
from deployer.log import DeployerLogger
from deployer.recipe import Recipe
from deployer.services import ServiceVersionWriter, RecipeReader
from features.steps.support import GIT_REPO_URL, TARGET_ENV, \
    TARGET_ENV_AND_NAMESPACE
from test.test_recipe import RecipeFileCreator

logger = DeployerLogger(__name__).getLogger()


@given("service is defined in source environment")
def write_service_to_int_git(context):
    prepare_recipe(context)
    ServiceVersionWriter(GIT_REPO_URL).write('kuku', Recipe.builder().ingredients(YamlReader().read(os.path.realpath(RecipeFileCreator.RECIPE))).build())
    delete_recipe()

def delete_recipe():
    try:
        os.remove(RecipeFileCreator.RECIPE)
    except OSError:
        pass


def prepare_recipe(context):
    with open(RecipeFileCreator.RECIPE, 'w') as outfile:
        yaml.dump({'image_name': '%sdeployer-test-java:1.0' % context.aws_uri}, outfile, default_flow_style=False)


@when("promoting to production")
def promote(context):
    assert os.system("python deployer/deployer.py promote --source kuku --target %s "
                     "--git_repository %s" % (TARGET_ENV_AND_NAMESPACE, GIT_REPO_URL)) == 0


@then("service should be logged in git")
def check_promoted_service_in_git(context):
    assert RecipeReader(GIT_REPO_URL).read(TARGET_ENV)[0].image() == '%sdeployer-test-java:1.0' % context.aws_uri

@then("expose property should be logged in git")
def check_expose_in_git(context):
    assert RecipeReader(GIT_REPO_URL).read(TARGET_ENV)[0].expose() is False

import os

import yaml
from behave import given, then, when
from deployer.log import DeployerLogger
from deployer.recipe import Recipe
from deployer.services import ServiceVersionWriter, ServiceVersionReader
from features.steps.support import JAVA_SERVICE_IMAGE_NAME, GIT_REPO_URL, TARGET_ENV, \
    TARGET_ENV_AND_NAMESPACE
from test.test_recipe import RecipeFileCreator

logger = DeployerLogger(__name__).getLogger()


@given("service is defined in source environment")
def write_service_to_int_git(context):
    prepare_recipe()
    ServiceVersionWriter(GIT_REPO_URL).write('kuku', Recipe.builder().indgredients(os.path.realpath(RecipeFileCreator.RECIPE)).build())
    delete_recipe()


def delete_recipe():
    try:
        os.remove(RecipeFileCreator.RECIPE)
    except OSError as e:
        print 'recipe path not found'


def prepare_recipe():
    with open(RecipeFileCreator.RECIPE, 'w') as outfile:
        yaml.dump({'image_name': JAVA_SERVICE_IMAGE_NAME}, outfile, default_flow_style=False)


@when("promoting to production")
def promote(context):
    assert os.system("python deployer/deployer.py promote --source kuku --target %s "
                     "--git_repository %s" % (TARGET_ENV_AND_NAMESPACE, GIT_REPO_URL)) == 0


@then("service should be logged in git")
def check_promoted_service_in_git(context):
    assert ServiceVersionReader(GIT_REPO_URL).read(TARGET_ENV)[0].image() == JAVA_SERVICE_IMAGE_NAME

@then("expose property should be logged in git")
def check_expose_in_git(context):
    assert ServiceVersionReader(GIT_REPO_URL).read(TARGET_ENV)[0].expose() is False

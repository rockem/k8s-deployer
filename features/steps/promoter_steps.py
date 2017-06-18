import os

import yaml
from behave import given, then, when
from behave import use_step_matcher

from deployer.file import YamlReader
from deployer.log import DeployerLogger
from deployer.recipe import Recipe
from deployer.services import ServiceVersionWriter, RecipeReader
from features.steps.support import GIT_REPO_URL, TARGET_ENV, \
    TARGET_ENV_AND_NAMESPACE
from features.support.context import Context
from features.support.deploy import DeployerDriver
from features.support.repository import RecipeRepository
from test.test_recipe import RecipeFileCreator

use_step_matcher("re")

logger = DeployerLogger(__name__).getLogger()

@given("\"(.*):(.*)\" service is defined in (.*) environment")
def write_service_to_int_git(context, name, version, env):
    app = Context(context).get_app_for(name, version)
    RecipeRepository().log_app(app)
    Context(context).set_last_deployed_app(app)

@when("promoting")
def promote(context):
    DeployerDriver(GIT_REPO_URL, TARGET_ENV_AND_NAMESPACE).promote()


@then("it should be logged in git")
def check_promoted_service_in_git(context):
    RecipeRepository().verify_app_is_logged(Context(context).last_deployed_app())


@then("recipe should be logged in git")
def check_expose_in_git(context):
    RecipeRepository().verify_recipe_is_logged_for(Context(context).last_deployed_app())

from behave import given, then, when
from behave import use_step_matcher
from features.support.context import Context
from features.support.deploy import DeployerDriver
from features.support.repository import RecipeRepository

use_step_matcher("re")


@given("\"(.*):(.*)\" service is defined in (.*) environment")
def write_service_to_int_git(context, name, version, env):
    app = Context(context).get_app_for(name, version)
    RecipeRepository().log_app(app)
    Context(context).set_last_deployed_app(app)


@when("promoting")
def promote(context):
    DeployerDriver(RecipeRepository.GIT_REPO_URL, Context(context).default_namespace(), context.domain,
                   Context(context).get_swagger_path()).promote()


@then("it should be logged in git")
def check_promoted_service_in_git(context):
    RecipeRepository().verify_app_is_logged(Context(context).last_deployed_app())


@then("recipe should be logged in git")
def check_expose_in_git(context):
    RecipeRepository().verify_recipe_is_logged_for(Context(context).last_deployed_app())

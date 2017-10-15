import os
from behave import given, then, when
from behave import use_step_matcher
from random_words import RandomWords

from features.support.context import Context
from features.support.deploy import DeployerDriver
from features.support.repository import LoggingRepository, SwaggerFileCreator

use_step_matcher("re")


@given("\"(.*):(.*)\" service is defined in (.*) environment")
def write_service_to_int_git(context, name, version, env):
    app = Context(context).get_app_for(name, version)
    LoggingRepository().log(LoggingRepository.recipe_location(env), LoggingRepository.recipe_content(app))
    Context(context).set_last_deployed_app(app)


@when("promoting from (.*) environment to int")
def promote(context,env):
    DeployerDriver(LoggingRepository.GIT_REPO_URL, Context(context).default_namespace(), context.domain).promote(env)


@then("it should be logged in git")
def check_promoted_service_in_git(context):
    LoggingRepository().verify_app_is_logged(Context(context).last_deployed_app())


@then("recipe should be logged in git")
def check_expose_in_git(context):
    LoggingRepository().verify_recipe_is_logged_for(Context(context).last_deployed_app())


@given("swagger is defined in (.*) environment")
def step_impl(context, env):
    random = RandomWords().random_word()
    SwaggerFileCreator().create_yml_with(random)
    LoggingRepository().log(LoggingRepository.swagger_location(env),LoggingRepository.SWAGGER_CONTENT)
    Context(context).add_swagger_response(random)
    print ("after update context : %s"%Context(context).get_swagger_response())





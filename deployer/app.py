import subprocess
import sys

import click
import os

from deploy import DeployError
from deploy import ImageDeployer
from k8s import K8sConnector
from log import DeployerLogger
from recipe import Recipe
from services import ServiceVersionWriter, RecipesReader, ConfigUploader, GlobalConfigFetcher
from util import EnvironmentParser, EnvironmentVariablesFetcher
from yml import YmlReader, SwaggerFileCreator

logger = DeployerLogger('deployer').getLogger()


class DeployCommand(object):
    def __init__(self, target, git_repository, domain, connector, recipe, timeout):
        self.target = target
        self.git_repository = git_repository
        self.recipe = recipe
        self.image_deployer = ImageDeployer(self.target, domain, connector, self.recipe, timeout)

    def run(self):
        logger.debug('is exposed %s ' % self.recipe.expose())
        self.__validate_image_contains_tag()
        self.image_deployer.deploy()
        ServiceVersionWriter(self.git_repository).write(EnvironmentParser(self.target).name(), self.recipe)
        logger.debug("finished deploying image:%s" % self.recipe.image())

    def __validate_image_contains_tag(self):
        if ':' not in self.recipe.image():
            logger.error('image_name should contain the tag')
            sys.exit(1)


class PromoteCommand(object):
    def __init__(self, from_env, to_env, git_repository, domain, connector, timeout):
        self.from_env = from_env
        self.to_env = to_env
        self.git_repository = git_repository
        self.domain = domain
        self.connector = connector
        self.timeout = timeout

    def run(self):
        recipes = RecipesReader(self.git_repository).read(self.from_env)
        for recipe in recipes:
            try:
                DeployCommand(self.to_env, self.git_repository, self.domain, self.connector, recipe, self.timeout).run()
            except DeployError as e:
                logger.warn("Failed to deploy %s with error: %s" % (recipe.image(), e.message))


class ConfigureCommand(object):
    def __init__(self, target, git_repository, connector):
        self.target = target
        self.git_repository = git_repository
        self.connector = connector

    def run(self):
        fetcher = GlobalConfigFetcher(self.git_repository)
        fetcher.checkout()

        ConfigUploader(self.connector).upload_config(
            fetcher.fetch_global_configuration_for(self.target))
        ConfigUploader(self.connector).upload_jobs(
            fetcher.fetch_jobs_for(self.target))

class SwaggerCommand(object):
    REST_API_ID = "REST_API_ID"

    def __init__(self,swagger_yml_path):
        self.swagger_yml_path = swagger_yml_path

    def run(self):
        self.create_rest_api()
        self.create_deployment()

    def __get_rest_api(self):
        return EnvironmentVariablesFetcher().fetch(self.REST_API_ID)

    def create_rest_api(self):

        subprocess.check_output("aws apigateway put-rest-api --rest-api-id %s --body %s "
                                   % (self.__get_rest_api(), 'file://'+SwaggerFileCreator(self.swagger_yml_path).create()), shell=True, stderr=subprocess.STDOUT)

    def create_deployment(self):
        subprocess.check_output("aws apigateway create-deployment --rest-api-id %s --stage-name %s"
                                   % (self.__get_rest_api(), EnvironmentVariablesFetcher().fetch("TARGET_ENV")), shell=True, stderr=subprocess.STDOUT)


class ActionRunner:
    def __init__(self, image_name, source, target, git_repository, domain, recipe_path, timeout,swagger_yml_path):
        self.image_name = image_name
        self.source = source
        self.target = target
        self.git_repository = git_repository
        self.domain = domain
        self.recipe_path = recipe_path
        self.timeout = timeout
        self.swagger_yml_path = swagger_yml_path

    def run(self, action):
        connector = K8sConnector(EnvironmentParser(self.target).namespace())
        if action == 'deploy':
            recipe = Recipe.builder().ingredients(YmlReader(self.recipe_path).read()).image(self.image_name).build()
            DeployCommand(self.target, self.git_repository, self.domain, connector, recipe, self.timeout).run()
        elif action == 'promote':
            PromoteCommand(self.source, self.target, self.git_repository, self.domain, connector, self.timeout).run()
        elif action == 'configure':
            ConfigureCommand(self.target, self.git_repository, connector).run()
        elif action == 'swagger':
            SwaggerCommand(self.swagger_yml_path).run()

@click.command()
@click.argument('action', type=click.Choice(['deploy', 'promote', 'configure','swagger']))
@click.option('--image_name', default=False)
@click.option('--source', default=False)
@click.option('--target')
@click.option('--git_repository')
@click.option('--domain', default="")
@click.option('--recipe', default="")
@click.option('--deploy-timeout', default=120)
@click.option('--swagger_yml_path', default="")

def main(action, image_name, source, target, git_repository, domain, recipe, deploy_timeout,swagger_yml_path):

    ActionRunner(image_name, source, target, git_repository, domain, recipe, deploy_timeout,swagger_yml_path).run(action)



if __name__ == "__main__":
    main()

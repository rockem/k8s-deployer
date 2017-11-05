import os
import sys

import click
import os

from aws import ApiGatewayConnector
from deploy import DeployError
from deploy import ImageDeployer
from git_util import GitClient
from k8s import K8sConnector
from log import DeployerLogger
from recipe import Recipe
from services import ConfigUploader, GlobalConfigFetcher
from repository import DeployLogRepository
from util import EnvironmentParser, ImageNameParser
from yml import YmlReader


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
        DeployLogRepository(self.git_repository).write(self.__recipe_location(), self.recipe.ingredients)
        logger.debug("finished deploying image:%s" % self.recipe.image())

    def __recipe_location(self):
        return os.path.join(EnvironmentParser(self.target).name(), "services",
                            "%s.yml" % ImageNameParser(self.recipe.image()).name())

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
        logger.debug('Starting Promoting ')
        recipes = DeployLogRepository(self.git_repository).read_from(self.__recipe_location())
        for recipe in recipes:
            r = Recipe.builder().ingredients(recipe).build()
            try:
                DeployCommand(self.to_env, self.git_repository,
                              self.domain,
                              self.connector,
                              r,
                              self.timeout).run()
            except DeployError as e:
                logger.warn("Failed to deploy %s with error: %s" % (r.image(), e.message))
        logger.debug('After Deploy')
        SwaggerCommand(self.__swagger_url(), self.git_repository).run()

    def __swagger_url(self):
        return DeployLogRepository(self.git_repository).read_from(self.__swagger_descriptor_location())['url']

    def __recipe_location(self):
        return os.path.join(GitClient.CHECKOUT_DIR, self.from_env, "services")

    def __swagger_descriptor_location(self):
        return os.path.join(GitClient.CHECKOUT_DIR, self.from_env, "api", "swagger.yml")


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
    def __init__(self, yml_path, git_repository):
        self.yml_path = yml_path
        self.git_repository = git_repository

    def run(self):
        logger.debug("start promote swagger" )
        SWAGGER_LOCATION = os.path.join(EnvironmentParser("").name(), "api", "swagger.yml")
        ApiGatewayConnector().upload_swagger(self.yml_path)
        DeployLogRepository(self.git_repository).write(SWAGGER_LOCATION, {'url': self.yml_path})
        logger.debug("finished promote swagger:%s" % SWAGGER_LOCATION)


class ActionRunner:
    def __init__(self, image_name, source, target, git_repository, domain, recipe_path, timeout, yml_path):
        self.image_name = image_name
        self.source = source
        self.target = target
        self.git_repository = git_repository
        self.domain = domain
        self.recipe_path = recipe_path
        self.timeout = timeout
        self.yml_path = yml_path

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
            SwaggerCommand(self.yml_path, self.git_repository).run()


@click.command()
@click.argument('action', type=click.Choice(['deploy', 'promote', 'configure', 'swagger']))
@click.option('--image_name', default=False)
@click.option('--source', default=False)
@click.option('--target')
@click.option('--git_repository')
@click.option('--domain', default="")
@click.option('--recipe', default="")
@click.option('--deploy-timeout', default=120)
@click.option('--yml_path', default="")
def main(action, image_name, source, target, git_repository, domain, recipe, deploy_timeout, yml_path):
    ActionRunner(image_name, source, target, git_repository, domain, recipe, deploy_timeout, yml_path).run(
        action)


if __name__ == "__main__":
    main()

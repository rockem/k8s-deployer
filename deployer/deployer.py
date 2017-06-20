import sys

import click
from kubectlconf.sync import S3ConfSync

from deploy import ImageDeployer
from deployer.deploy import DeployError
from services import ServiceVersionWriter, RecipeReader, ConfigUploader, GlobalConfigFetcher
from file import YamlReader
from k8s import Connector
from log import DeployerLogger
from recipe import Recipe
from util import EnvironmentParser

logger = DeployerLogger('deployer').getLogger()


class DeployCommand(object):
    def __init__(self, target, git_repository, connector, recipe):
        self.target = target
        self.git_repository = git_repository
        self.recipe = recipe
        self.image_deployer = ImageDeployer(self.recipe.image(), self.target, connector, self.recipe)

    def run(self):
        logger.debug('is exposed %s ' % self.recipe.expose())
        self.__validate_image_contains_tag()
        self.image_deployer.deploy()
        ServiceVersionWriter(self.git_repository).write(EnvironmentParser(self.target).env_name(), self.recipe)
        logger.debug("finished deploying image:%s" % self.recipe.image())

    def __validate_image_contains_tag(self):
        if ':' not in self.recipe.image():
            logger.error('image_name should contain the tag')
            sys.exit(1)


class PromoteCommand(object):
    def __init__(self, from_env, to_env, git_repository, connector):
        self.from_env = from_env
        self.to_env = to_env
        self.git_repository = git_repository
        self.connector = connector

    def run(self):
        recipes = RecipeReader(self.git_repository).read(self.from_env)
        for recipe in recipes:
            try:
                DeployCommand(self.to_env, self.git_repository, self.connector, recipe).run()
            except DeployError as e:
                logger.warn("Failed to deploy %s with error: %s" % (recipe.image(), e.message))


class ConfigureCommand(object):
    def __init__(self, target, git_repository, connector):
        self.target = target
        self.git_repository = git_repository
        self.connector = connector

    def run(self):
        ConfigUploader(self.target, self.connector).upload(
            GlobalConfigFetcher(self.git_repository).fetch_for(self.target))


class ActionRunner:
    def __init__(self, image_name, source, target, git_repository, recipe_path):
        self.image_name = image_name
        self.source = source
        self.target = target
        self.git_repository = git_repository
        self.recipe_path = recipe_path

    def run(self, action):
        self.__update_kubectl()
        connector = Connector(EnvironmentParser(self.target).namespace())
        if action == 'deploy':
            recipe = Recipe.builder().ingredients(YamlReader().read(self.recipe_path)).image(self.image_name).build()
            DeployCommand(self.target, self.git_repository, connector, recipe).run()
        elif action == 'promote':
            PromoteCommand(self.source, self.target, self.git_repository, connector).run()
        elif action == 'configure':
            ConfigureCommand(self.target, self.git_repository, connector).run()

    def __update_kubectl(self):
        S3ConfSync(EnvironmentParser(self.target).env_name()).sync()


@click.command()
@click.argument('action', type=click.Choice(['deploy', 'promote', 'configure']))
@click.option('--image_name', default=False)
@click.option('--source', default=False)
@click.option('--target')
@click.option('--git_repository')
@click.option('--recipe')
def main(action, image_name, source, target, git_repository, recipe):
    ActionRunner(image_name, source, target, git_repository, recipe).run(action)


if __name__ == "__main__":
    main()

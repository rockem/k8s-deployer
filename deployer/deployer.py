import sys

import click
import subprocess
from kubectlconf.sync import S3ConfSync

from deploy import ImageDeployer
from k8s import Connector
from log import DeployerLogger
from recipe import Recipe
from services import ConfigUploader, GlobalConfigFetcher
from services import ServiceVersionReader, ServiceVersionWriter
from util import EnvironmentParser

logger = DeployerLogger('deployer').getLogger()


class DeployCommand(object):
    def __init__(self, image_name, target, git_repository, connector, recipe):
        logger.debug('recipe path %s ' % recipe)
        self.read_file(recipe)
        self.image_name = image_name
        self.target = target
        self.git_repository = git_repository
        self.recipe = Recipe.builder().ingredients(recipe).image(self.image_name).build()
        self.image_deployer = ImageDeployer(self.image_name, self.target, connector, self.recipe)

    def read_file(self, path):
        try:
            output = subprocess.check_output('ls -ltr', shell=True)
            logger.info('ls -ltr: %s' % output)
            logger.info('str(path): %s' % str(path))
            content = open(str(path), "r")
            logger.debug("this is the file content %s" % content)
        except IOError as e:
            logger.exception("We could not open the file!")
            return {}

    def run(self):
        logger.debug('is exoised %s ' % self.recipe.expose())
        self.__validate_image_contains_tag()
        self.image_deployer.deploy()
        ServiceVersionWriter(self.git_repository).write(EnvironmentParser(self.target).env_name(), self.recipe)
        logger.debug("finished deploying image:%s" % self.image_name)

    def __validate_image_contains_tag(self):
        if ':' not in self.image_name:
            logger.error('image_name should contain the tag')
            sys.exit(1)


class PromoteCommand(object):
    def __init__(self, from_env, to_env, git_repository, connector):
        self.from_env = from_env
        self.to_env = to_env
        self.git_repository = git_repository
        self.connector = connector

    def run(self):
        recipes = ServiceVersionReader(self.git_repository).read(self.from_env)
        for recipe in recipes:
            logger.debug('recipe %s' % recipe.ingredients)
            DeployCommand(recipe.image(), self.to_env, self.git_repository, self.connector, recipe).run()


class ConfigureCommand(object):
    def __init__(self, target, git_repository, connector):
        self.target = target
        self.git_repository = git_repository
        self.connector = connector

    def run(self):
        ConfigUploader(self.target, self.connector).upload(
            GlobalConfigFetcher(self.git_repository).fetch_for(self.target))


class ActionRunner:
    def __init__(self, image_name, source, target, git_repository, recipe):
        self.image_name = image_name
        self.source = source
        self.target = target
        self.git_repository = git_repository
        self.recipe = recipe

    def run(self, action):
        self.__update_kubectl()
        connector = Connector(EnvironmentParser(self.target).namespace())
        if action == 'deploy':
            DeployCommand(self.image_name, self.target, self.git_repository, connector, self.recipe).run()
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

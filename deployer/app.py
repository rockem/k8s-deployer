import sys

import click
import os

from aws import ApiGatewayConnector
from deploy import DeployError
from deploy import ImageDeployer
from k8s import K8sConnector
from log import DeployerLogger
from recipe import Recipe
from services import ConfigUploader, GlobalConfigFetcher
from repository import DeployLogRepository
from util import EnvironmentParser, ImageNameParser
from yml import YmlReader

logger = DeployerLogger('deployer').getLogger()


def recipe_location(env, recipe):
    return os.path.join(EnvironmentParser(env).name(), "services",
                        "%s.yml" % ImageNameParser(recipe.image()).name())


class WriteToLogCommand(object):
    def __init__(self, git_repository, env, recipe, command):
        self.git_repository = git_repository
        self.env = env
        self.recipe = recipe
        self.command = command

    def run(self):
        self.run_pre_command()
        DeployLogRepository(self.git_repository).write(recipe_location(self.env, self.recipe), self.recipe
                                                       .ingredients)

    def run_pre_command(self):
        try:
            self.command.run()
        except Exception as e:
            raise e


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
        recipes = DeployLogRepository(self.git_repository, self.from_env).get_all_recipes()
        for recipe in recipes:
            r = Recipe.builder().ingredients(recipe).build()
            WriteToLogCommand(self.git_repository, self.to_env, r,
                                  DeployCommand(self.to_env, self.git_repository,
                                                self.domain,
                                                self.connector,
                                                r,
                                                self.timeout)).run()


        logger.debug('After Deploy')
        SwaggerCommand(self.__swagger_url(), self.git_repository).run()

    def __swagger_url(self):
        return DeployLogRepository(self.git_repository, self.from_env).get_swagger()['url']


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
        swagger_location = os.path.join(EnvironmentParser("").name(), "api", "swagger.yml")
        ApiGatewayConnector().upload_swagger(self.yml_path)
        DeployLogRepository(self.git_repository, None).write(swagger_location, {'url': self.yml_path})
        logger.debug("finished promote swagger:%s" % swagger_location)


class RollbackCommand(object):
    def __init__(self, target, git_repo, domain, connector, timeout, service_name):
        self.git_repository = git_repo
        self.target = target
        self.deploy_log = DeployLogRepository(git_repo, EnvironmentParser(self.target).name())
        self.connector = connector
        self.timeout = timeout
        self.domain = domain
        self.service_name = service_name

    def run(self):
        logger.info("going to rollback target = %s, service_name = %s" % (self.target, self.service_name))
        recipe = self.deploy_log.get_previous_recipe(self.service_name)
        r = Recipe.builder().ingredients(recipe).build()
        WriteToLogCommand(self.git_repository, EnvironmentParser(self.target).name(), r,
                          DeployCommand(self.target,
                                        self.git_repository,
                                        self.domain,
                                        self.connector,
                                        Recipe.builder().ingredients(recipe).build(),
                                        self.timeout)).run()



class ActionRunner:
    def __init__(self, image_name, source, target, git_repository, domain, recipe_path, timeout, yml_path,
                 service_name):
        self.image_name = image_name
        self.source = source
        self.target = target
        self.git_repository = git_repository
        self.domain = domain
        self.recipe_path = recipe_path
        self.timeout = timeout
        self.yml_path = yml_path
        self.service_name = service_name

    def run(self, action):
        connector = K8sConnector(EnvironmentParser(self.target).namespace())
        if action == 'deploy':
            recipe = Recipe.builder().ingredients(YmlReader(self.recipe_path).read()).image(self.image_name).build()
            WriteToLogCommand(self.git_repository, EnvironmentParser(self.target).name(), recipe,
                           DeployCommand(self.target, self.git_repository, self.domain, connector, recipe, self.timeout)).run()

        elif action == 'promote':
            PromoteCommand(self.source, self.target, self.git_repository, self.domain, connector, self.timeout).run()
        elif action == 'configure':
            ConfigureCommand(self.target, self.git_repository, connector).run()
        elif action == 'swagger':
            SwaggerCommand(self.yml_path, self.git_repository).run()
        elif action == 'rollback':
            RollbackCommand(self.target, self.git_repository, self.domain, connector, self.timeout,
                            self.service_name).run()
        else:
            raise DeployError('Unknown command %s' % action)


@click.command()
@click.argument('action', type=click.Choice(['deploy', 'promote', 'configure', 'swagger', 'rollback']))
@click.option('--image_name', default=False)
@click.option('--source', default=False)
@click.option('--target')
@click.option('--git_repository')
@click.option('--domain', default="")
@click.option('--recipe', default="")
@click.option('--deploy-timeout', default=120)
@click.option('--yml_path', default="")
@click.option('--service_name', default="")
def main(action, image_name, source, target, git_repository, domain, recipe, deploy_timeout, yml_path, service_name):
    ActionRunner(image_name, source, target, git_repository, domain, recipe, deploy_timeout, yml_path,
                 service_name).run(
        action)


if __name__ == "__main__":
    main()





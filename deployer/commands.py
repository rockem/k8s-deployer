import os
import sys

from deploy import ImageDeployer
from log import DeployerLogger
from protected_rollback_proxy import ProtectedRollbackProxy
from recipe import Recipe
from services import ConfigUploader, GlobalConfigFetcher
from util import EnvironmentParser, ImageNameParser

logger = DeployerLogger('deployer').getLogger()


def recipe_location(env, recipe):
    return os.path.join(EnvironmentParser(env).name(), "services",
                        "%s.yml" % ImageNameParser(recipe.image()).name())


class WriteToLogCommand(object):
    def __init__(self, deploy_command):
        self.deploy_command = deploy_command

    def post_run(self): pass

    def run(self):
        self.deploy_command.run()
        self.post_run()


class WriteToLogCommandRegularDeploy(WriteToLogCommand):
    def __init__(self, mongo_connector, recipe, env, deploy_command):
        super(WriteToLogCommandRegularDeploy, self).__init__(deploy_command)
        self.mongo_log_repository = ProtectedRollbackProxy(mongo_connector, env, ImageNameParser(recipe.image()).name())
        self.recipe = recipe

    def post_run(self):
        self.mongo_log_repository.write_deployment(self.recipe.ingredients)


class WriteToLogCommandRollback(WriteToLogCommand):
    def __init__(self, mongo_connector, env, service_name, deploy_command):
        super(WriteToLogCommandRollback, self).__init__(deploy_command)
        self.mongo_log_repository = ProtectedRollbackProxy(mongo_connector, env, service_name)

    def post_run(self):
        self.mongo_log_repository.rollback()


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
    def __init__(self, from_env, to_env, git_repository, domain, connector, timeout, mongo_connector):
        self.from_env = from_env
        self.to_env = to_env
        self.git_repository = git_repository
        self.domain = domain
        self.connector = connector
        self.timeout = timeout
        self.mongo_connector = mongo_connector

    def run(self):
        recipes = ProtectedRollbackProxy(self.mongo_connector, self.from_env).get_all_recipes()
        for recipe in recipes:
            r = Recipe.builder().ingredients(recipe).build()
            WriteToLogCommandRegularDeploy(self.mongo_connector, r, self.to_env,
                                           DeployCommand(self.to_env, self.git_repository,
                                                         self.domain,
                                                         self.connector,
                                                         r,
                                                         self.timeout)).run()


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

class RollbackCommand(object):
    def __init__(self, target, git_repo, domain, connector, timeout, service_name, mongo_connector):
        self.git_repository = git_repo
        self.target = target
        self.connector = connector
        self.timeout = timeout
        self.domain = domain
        self.service_name = service_name
        self.mongo_connector = mongo_connector

    def run(self):
        logger.info("going to rollback target = %s, service_name = %s" % (self.target, self.service_name))

        env = EnvironmentParser(self.target).name()
        mongo_repository = ProtectedRollbackProxy(self.mongo_connector, env, self.service_name)

        recipe = Recipe.builder().ingredients(mongo_repository.get_previous_recipe()).build()

        WriteToLogCommandRollback(self.mongo_connector, env,
                                  self.service_name,
                                  DeployCommand(self.target,
                                                self.git_repository,
                                                self.domain,
                                                self.connector,
                                                recipe,
                                                self.timeout)).run()

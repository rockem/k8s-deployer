import os
import sys

from deploy import ImageDeployer
from repository import DummyMongoConnector, MongoDeploymentRepository
from yml import YmlReader
from k8s import K8sConnector
from log import DeployerLogger
from protected_rollback_proxy import ProtectedRollbackProxy
from recipe import Recipe
from services import ConfigUploader, GlobalConfigFetcher
from util import EnvironmentParser, ImageNameParser

logger = DeployerLogger('deployer').getLogger()


def recipe_location(env, recipe):
    return os.path.join(EnvironmentParser(env).name(), "services",
                        "%s.yml" % ImageNameParser(recipe.image()).name())


class BaseCommand():
    def __init__(self, mongo_uri, target):
        self.mongo_connector = self.__get_mongo_connector(mongo_uri)
        self.connector = K8sConnector(EnvironmentParser(target).namespace())

    def __get_mongo_connector(self, mongo_uri):
        return DummyMongoConnector() if mongo_uri == '' else MongoDeploymentRepository(mongo_uri)


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


class DeployProcess(object):
    def __init__(self, args, connector, recipe):
        self.git_repository = args["git_repository"]
        self.recipe = recipe
        self.image_deployer = ImageDeployer(args, connector, self.recipe)

    def run(self):
        logger.debug('is exposed %s ' % self.recipe.expose())
        self.__validate_image_contains_tag()
        self.image_deployer.deploy()
        logger.debug("finished deploying image:%s" % self.recipe.image())

    def __validate_image_contains_tag(self):
        if ':' not in self.recipe.image():
            logger.error('image_name should contain the tag')
            sys.exit(1)


class DeploymentCommand(BaseCommand, object):
    def __init__(self, args):
        super(DeploymentCommand, self).__init__(args["mongo_uri"], args["target"])
        self.args = args
        self.from_env = args["source"]
        self.to_env = args["target"]

    def run(self):
        recipe = Recipe.builder().ingredients(YmlReader(self.args["recipe"]).read()).image(
            self.args["image_name"]).build()
        env = EnvironmentParser(self.args["target"]).name()
        WriteToLogCommandRegularDeploy(self.mongo_connector, recipe, env,
                                       DeployProcess(self.args, self.connector,
                                                     recipe)).run()


class PromoteCommand(BaseCommand, object):
    def __init__(self, args):
        super(PromoteCommand, self).__init__(args["mongo_uri"], args["target"])
        self.args = args
        self.from_env = args["source"]
        self.to_env = args["target"]

    def run(self):
        recipes = ProtectedRollbackProxy(self.mongo_connector, self.from_env).get_all_recipes()
        for recipe in recipes:
            r = Recipe.builder().ingredients(recipe).build()
            WriteToLogCommandRegularDeploy(self.mongo_connector, r, self.to_env,
                                           DeployProcess(self.args,
                                                         self.connector,
                                                         r)).run()


class ConfigureCommand(BaseCommand, object):
    def __init__(self, args):
        super(ConfigureCommand, self).__init__(args["mongo_uri"], args["target"])
        self.target = args["target"]
        self.git_repository = args["git_repository"]

    def run(self):
        fetcher = GlobalConfigFetcher(self.git_repository)
        fetcher.checkout()
        ConfigUploader(self.connector).upload_config(
            fetcher.fetch_global_configuration_for(self.target))


class RollbackCommand(BaseCommand, object):
    def __init__(self, args):
        super(RollbackCommand, self).__init__(args["mongo_uri"], args["target"])
        self.args = args
        self.git_repository = args["git_repository"]
        self.target = args["target"]
        self.service_name = args["service_name"]

    def run(self):
        logger.info("going to rollback target = %s, service_name = %s" % (self.target, self.service_name))
        env = EnvironmentParser(self.args["target"]).name()
        mongo_repository = ProtectedRollbackProxy(self.mongo_connector, env, self.service_name)
        recipe = Recipe.builder().ingredients(mongo_repository.get_previous_recipe()).build()

        WriteToLogCommandRollback(self.mongo_connector, env,
                                  self.service_name,
                                  DeployProcess(self.args,
                                                self.connector,
                                                recipe)).run()

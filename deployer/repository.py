import os

import yaml

from deployer.git_util import GitClient
from deployer.recipe import Recipe
from deployer.services import logger, SERVICES_FOLDER
from deployer.util import create_directory
from deployer.yml import YmlReader


class DeployLogRepository:

    def __init__(self, git_repository):
        self.git_client = GitClient(git_repository)

    def write(self, path, data):
        self.git_client.checkout()
        logger.debug("git url for push! %s")
        DeployLogRepository.__write_service_file(path, data)
        self.git_client.check_in()

    @staticmethod
    def __write_service_file(path, data):
        create_directory(os.path.join(GitClient.CHECKOUT_DIR, os.path.dirname(path)))
        with(open(os.path.join(GitClient.CHECKOUT_DIR, path), 'w')) as service_file:
            yaml.dump(data, service_file, default_flow_style=False, allow_unicode=False)

    def read(self, from_env):
        self.git_client.checkout()
        return self.__gather_recipes(os.path.join(GitClient.CHECKOUT_DIR, from_env, SERVICES_FOLDER))

    def __gather_recipes(self, services_path):
        recipes = []
        for dir in os.listdir(services_path):
            logger.debug('recipe is %s' % os.path.join(services_path, dir))
            recipes.append(
                Recipe.builder().ingredients(YmlReader(os.path.join(services_path, dir)).read()).build())
        return recipes
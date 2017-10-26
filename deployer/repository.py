import os

import yaml

from git_util import GitClient
from recipe import Recipe
from services import logger, SERVICES_FOLDER
from util import create_directory
from yml import YmlReader


class DeployLogRepository:

    def __init__(self, git_repository):
        self.git_client = GitClient(git_repository)
        self.git_client.checkout()

    def write(self, path, data):
        logger.debug("git url for push! %s"%path)
        DeployLogRepository.__write_service_file(path, data)
        self.git_client.check_in()

    @staticmethod
    def __write_service_file(path, data):
        create_directory(os.path.join(GitClient.CHECKOUT_DIR, os.path.dirname(path)))
        with(open(os.path.join(GitClient.CHECKOUT_DIR, path), 'w')) as service_file:
            yaml.dump(data, service_file, default_flow_style=False, allow_unicode=False)

    def read_from(self, location):
        return self.__gather_recipes(location)

    def __gather_recipes(self, location):
        recipes = []

        if(os.path.isfile(location)):
            return  YmlReader(location).read()

        for dir in os.listdir(location):
            logger.debug('recipe is %s' % os.path.join(location, dir))
            recipes.append(YmlReader(os.path.join(location, dir)).read())
        return recipes


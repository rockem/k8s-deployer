import os
import yaml
from git_util import GitClient
from services import logger
from util import create_directory
from yml import YmlReader


class DeployLogRepository:
    def __init__(self, git_repository, env=None):
        self.git_client = GitClient(git_repository)
        self.git_client.checkout()
        self.env = env

    def write(self, path, data):
        logger.debug("git url for push! %s" % path)
        DeployLogRepository.__write_service_file(path, data)
        self.git_client.check_in()

    @staticmethod
    def __write_service_file(path, data):
        create_directory(os.path.join(GitClient.CHECKOUT_DIR, os.path.dirname(path)))
        with(open(os.path.join(GitClient.CHECKOUT_DIR, path), 'w')) as service_file:
            yaml.dump(data, service_file, default_flow_style=False, allow_unicode=False)

    def get_all_recipes(self):
        return self.__gather_recipes(os.path.join(GitClient.CHECKOUT_DIR, self.env, "services"))

    @staticmethod
    def __gather_recipes(location):
        recipes = []

        if os.path.isfile(location):
            return YmlReader(location).read()

        if os.path.isdir(location):
            for dir in os.listdir(location):
                logger.debug('recipe is %s' % os.path.join(location, dir))
                recipes.append(YmlReader(os.path.join(location, dir)).read())

        return recipes

    def get_previous_recipe(self, file_name):
        path = os.path.join(self.env, 'services', file_name + '.yml')
        return yaml.load(self.git_client.retrieve_previous_commit_file(path))

    def get_swagger(self):
        path = os.path.join(GitClient.CHECKOUT_DIR, self.env, 'api', 'swagger.yml')
        return YmlReader(path).read()

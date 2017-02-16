import os

import yaml

from recipe import Recipe
from gitclient.git_client import GitClient
from log import DeployerLogger
from util import create_directory, EnvironmentParser, ImageNameParser

logger = DeployerLogger(__name__).getLogger()

SERVICES_FOLDER = 'services'


class ServiceVersionWriter:
    def __init__(self, git_repository):
        self.git_client = GitClient(git_repository)

    def write(self, target, recipe):
        self.git_client.checkout()
        logger.debug("git url for push! %s")
        file_name = os.path.join(target, SERVICES_FOLDER, "%s.yml" % ImageNameParser(recipe.image()).name())
        self.__write_service_file(file_name, recipe)
        self.git_client.check_in()

    def __write_service_file(self, file_name, recipe):
        create_directory(os.path.join(GitClient.CHECKOUT_DIR, os.path.dirname(file_name)))
        service_file = open(os.path.join(GitClient.CHECKOUT_DIR, file_name), 'w')
        yaml.dump(recipe.indgredients, service_file, default_flow_style=False)
        service_file.close()


class ServiceVersionReader:
    def __init__(self, git_repository):
        self.git_client = GitClient(git_repository)

    def read(self, from_env):
        self.git_client.checkout()
        return self.__get_recipes(os.path.join(GitClient.CHECKOUT_DIR, from_env, SERVICES_FOLDER))

    def __get_recipes(self, services_path):
        recipes = []
        for filename in os.listdir(services_path):
            srv_yml_file = open(os.path.join(services_path, filename), 'r')
            yml = yaml.load(srv_yml_file)
            recipes.append(Recipe(yml))
        return recipes

class ConfigUploader:
    def __init__(self, target, connector):
        self.target = target
        self.connector = connector

    def upload(self, config_file_path):
        self.connector.upload_config_map(config_file_path)

class GlobalConfigFetcher:
    def __init__(self, git_repository):
        self.git_client = GitClient(git_repository)

    def fetch_for(self, target):
        self.git_client.checkout()
        env_name = EnvironmentParser(target).env_name()

        return os.path.join(GitClient.CHECKOUT_DIR, env_name, 'global.yml')

import os

from git_util import GitClient
from log import DeployerLogger
from util import EnvironmentParser
from yml import YmlReader

logger = DeployerLogger(__name__).getLogger()

SERVICES_FOLDER = 'services'


class ConfigUploader:
    def __init__(self, connector):
        self.connector = connector

    def upload_config(self, config_file_path):
        self.connector.upload_config_map(config_file_path)


class GlobalConfigFetcher:
    def __init__(self, git_repository):
        self.git_client = GitClient(git_repository)

    def checkout(self):
        self.git_client.checkout()

    def fetch_global_configuration_for(self, target):
        return self.__fetch_for(target, 'global-configs')

    def fetch_jobs_for(self, target):
        return self.__fetch_for(target, 'jobs.yml')

    def __fetch_for(self, target, file_name):
        env_name = EnvironmentParser(target).name()
        return os.path.join(GitClient.CHECKOUT_DIR, env_name, file_name)

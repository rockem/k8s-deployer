import os

import yaml

from git_util import GitClient
from yml import YmlReader
from log import DeployerLogger
from recipe import Recipe
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
        with(open(os.path.join(GitClient.CHECKOUT_DIR, file_name), 'w')) as service_file:
            yaml.dump(recipe.ingredients, service_file, default_flow_style=False, allow_unicode=False)


class RecipesReader:
    def __init__(self, git_repository):
        self.git_client = GitClient(git_repository)

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


class ConfigUploader:
    def __init__(self, connector):
        self.connector = connector

    def upload_config(self, config_file_path):
        self.connector.upload_config_map(config_file_path)

    def upload_jobs(self, jobs_file_path): 
        if jobs_file_path is not None:
            jobs_list = self.create_jobs_from(jobs_file_path)
            for job in jobs_list:
                self.connector.upload_job(job)

    def create_jobs_from(self, jobs_file_path):
        jobs_list = []
        logger.info('Going to read the jobs from file \'%s\'' % jobs_file_path)
        content = YmlReader(jobs_file_path).read()
        for item in content['jobs']:
            job_name = next(iter(item))
            jobs_list.append( {'name': job_name,
                            'schedule': item[job_name]['schedule'],
                            'url': item[job_name]['url']})

        return jobs_list


class GlobalConfigFetcher:
    def __init__(self, git_repository):
        self.git_client = GitClient(git_repository)

    def checkout(self):
        self.git_client.checkout()

    def fetch_global_configuration_for(self, target):
        return self.__fetch_for(target, 'global.yml')

    def fetch_jobs_for(self, target):
        return self.__fetch_for(target, 'jobs.yml')

    def __fetch_for(self, target, file_name):
        env_name = EnvironmentParser(target).name()
        return os.path.join(GitClient.CHECKOUT_DIR, env_name, file_name)

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
        return self.__fetch_for(target, 'global-configs')

    def fetch_jobs_for(self, target):
        return self.__fetch_for(target, 'jobs.yml')

    def __fetch_for(self, target, file_name):
        env_name = EnvironmentParser(target).name()
        return os.path.join(GitClient.CHECKOUT_DIR, env_name, file_name)

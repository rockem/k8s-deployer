import os

import yaml

from log import DeployerLogger
from gitclient.GitClient import GitClient

logger = DeployerLogger(__name__).getLogger()


class ServiceVersionWriter:
    CHECKOUT_DIRECTORY = 'tmp'
    # SERVICES_ENVS_REPO = 'https://git.dnsk.io/media-platform/k8s-services-envs'
    SERVICES_FOLDER = '/services/'
    IMAGE_NAME = 'image_name'
    git_client = GitClient()

    def __init__(self, git_repository):
        self.git_url = git_repository

    def write(self, to, service_name, image_name):
        self.git_client.delete_checkout_dir(self.CHECKOUT_DIRECTORY)
        repo = self.git_client.get_repo(self.git_url, self.CHECKOUT_DIRECTORY)
        srv_directory = to + self.SERVICES_FOLDER
        self.git_client.create_directory(self.CHECKOUT_DIRECTORY + '/' + srv_directory)
        file_name = srv_directory + service_name + '.yml'
        self.__write_service_file(self.CHECKOUT_DIRECTORY, file_name, image_name)
        self.git_client.push(file_name, repo, service_name, image_name)
        logger.info('finished updating repository(if necessary):%s with environment:%s, service name:%s and image:%s'
                    % (self.git_url, to, service_name, image_name))

    def __write_service_file(self, checkout_directory, file_name, image_name):
        service_file = open(checkout_directory + '/' + file_name, 'w')
        service_file.write(self.IMAGE_NAME + ': %s' % image_name)
        service_file.close()


class ServiceVersionReader:
    CHECKOUT_DIRECTORY = 'tmp'
    # SERVICES_ENVS_REPO = 'https://git.dnsk.io/media-platform/k8s-services-envs'
    SERVICES_FOLDER = '/services/'
    IMAGE_NAME = 'image_name'

    git_client = GitClient()

    def __init__(self, git_repository):
        self.git_url = git_repository

    def read(self, from_env):
        self.git_client.delete_checkout_dir(self.CHECKOUT_DIRECTORY)
        self.git_client.get_repo(self.git_url, self.CHECKOUT_DIRECTORY)
        return self.__get_images_to_deploy(self.CHECKOUT_DIRECTORY + '/' + from_env + self.SERVICES_FOLDER)

    def __get_images_to_deploy(self, services_path):
        images_to_deploy = []
        for filename in os.listdir(services_path):
            file_path = os.path.join(services_path, filename)
            srv_yml_file = open(file_path, 'r')
            image_dict = yaml.load(srv_yml_file)
            image_name = image_dict.get(self.IMAGE_NAME)
            images_to_deploy.append(image_name)
        return images_to_deploy

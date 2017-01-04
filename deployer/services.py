import os

import yaml

from log import DeployerLogger
from gitclient.git_client import GitClient

logger = DeployerLogger(__name__).getLogger()

CHECKOUT_DIRECTORY = 'tmp'
SERVICES_FOLDER = '/services/'
IMAGE_NAME = 'image_name'
git_client = GitClient()


class ServiceVersionWriter:
    def __init__(self, git_repository):
        self.git_url = git_repository

    def write(self, target, service_name, image_name):
        srv_directory = target + SERVICES_FOLDER
        repo = self.__init_checkout_dir()
        file_name = srv_directory + service_name + '.yml'
        self.__write_service_file(file_name, image_name, srv_directory)
        git_client.push(file_name, repo, service_name, image_name)
        logger.info('finished updating repository(if necessary):%s with environment:%s, service name:%s and image:%s'
                    % (self.git_url, target, service_name, image_name))

    def __init_checkout_dir(self):
        logger.info("delete tmp")
        git_client.delete_checkout_dir(CHECKOUT_DIRECTORY)
        return git_client.get_repo(self.git_url, CHECKOUT_DIRECTORY)

    def __write_service_file(self, file_name, image_name, srv_directory):
        git_client.create_directory(CHECKOUT_DIRECTORY + '/' + srv_directory)
        service_file = open(CHECKOUT_DIRECTORY + '/' + file_name, 'w')
        service_file.write(IMAGE_NAME + ': %s' % image_name)
        service_file.close()


class ServiceVersionReader:
    def __init__(self, git_repository):
        self.git_url = git_repository

    def read(self, from_env):
        git_client.delete_checkout_dir(CHECKOUT_DIRECTORY)
        git_client.get_repo(self.git_url, CHECKOUT_DIRECTORY)
        return self.__get_images_to_deploy(CHECKOUT_DIRECTORY + '/' + from_env + SERVICES_FOLDER)

    def __get_images_to_deploy(self, services_path):
        images_to_deploy = []
        for filename in os.listdir(services_path):
            srv_yml_file = open(os.path.join(services_path, filename), 'r')
            images_to_deploy.append(self.__get_image_name(srv_yml_file))
        return images_to_deploy

    def __get_image_name(self, srv_yml_file):
        image_dict = yaml.load(srv_yml_file)
        image_name = image_dict.get(IMAGE_NAME)
        return image_name

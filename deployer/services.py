import os

import subprocess
import yaml

from util import create_directory, EnvironmentParser
from log import DeployerLogger
from gitclient.git_client import GitClient, CHECKOUT_DIR

logger = DeployerLogger(__name__).getLogger()

SERVICES_FOLDER = 'services'
IMAGE_LABEL = 'image_name'


class ServiceVersionWriter:
    def __init__(self, git_repository):
        self.git_client = GitClient(git_repository)

    def write(self, target, service_name, image_name):
        self.git_client.checkout()
        file_name = os.path.join(target, SERVICES_FOLDER, "%s.yml" % service_name)
        self.__write_service_file(file_name, image_name)
        self.git_client.check_in()

    def __write_service_file(self, file_name, image_name):
        create_directory(os.path.join(CHECKOUT_DIR, os.path.dirname(file_name)))
        service_file = open(os.path.join(CHECKOUT_DIR, file_name), 'w')
        service_file.write('%s: %s' % (IMAGE_LABEL, image_name))
        service_file.close()


class ServiceVersionReader:
    def __init__(self, git_repository):
        self.git_client = GitClient(git_repository)

    def read(self, from_env):
        self.git_client.checkout()
        return self.__get_images_to_deploy(os.path.join(CHECKOUT_DIR, from_env, SERVICES_FOLDER))

    def __get_images_to_deploy(self, services_path):
        images_to_deploy = []
        for filename in os.listdir(services_path):
            srv_yml_file = open(os.path.join(services_path, filename), 'r')
            images_to_deploy.append(self.__get_image_name(srv_yml_file))
        return images_to_deploy

    def __get_image_name(self, srv_yml_file):
        image_dict = yaml.load(srv_yml_file)
        image_name = image_dict.get(IMAGE_LABEL)
        return image_name


class ConfigUploader:
    def __init__(self, target):
        self.target = target

    def upload(self, config_file_path):
        namespace = EnvironmentParser(self.target).namespace()
        os.system("kubectl delete configmap global-config --namespace=%s" % namespace)
        subprocess.check_output("kubectl create configmap global-config --from-file=%s --namespace=%s"
                                % (config_file_path, namespace), shell=True)


class GlobalConfigFetcher:
    def __init__(self, git_repository):
        self.git_client = GitClient(git_repository)

    def fetch_for(self, target):
        self.git_client.checkout()
        env_name = EnvironmentParser(target).env_name()

        return os.path.join(CHECKOUT_DIR, env_name, 'global.yml')

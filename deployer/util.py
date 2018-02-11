import os
import re


class ImageNameParser(object):
    SERVICE_NAME_PATTERN = r'^(.*/)?(.+):'

    def __init__(self, image_name):
        self.image_name = image_name

    def name(self):
        return re.search(self.SERVICE_NAME_PATTERN, self.image_name).group(2)



class EnvironmentVariablesFetcher(object):
    def fetch(self, key):
        return os.environ.get(key)


class EnvironmentParser(object):
    DEFAULT_NAMESPACE = 'default'

    def __init__(self, target_namespace):
        self.env_variable_fetcher = EnvironmentVariablesFetcher()
        self.target_namespace = self.DEFAULT_NAMESPACE if self.__is_default(target_namespace) else target_namespace

    def namespace(self):
        return self.target_namespace

    def __is_default(self, target_namespace):
        return target_namespace == '' or target_namespace == None

    def name(self):
        return self.env_variable_fetcher.fetch('TARGET_ENV')

    def env(self):
        return "{0}:{1}".format(self.name(), self.target_namespace)


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

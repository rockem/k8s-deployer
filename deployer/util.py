import os
import re


class ImageNameParser(object):
    SERVICE_NAME_PATTERN = r'^(.*/)?(.+):'

    def __init__(self, image_name):
        self.image_name = image_name

    def name(self):
        return re.search(self.SERVICE_NAME_PATTERN, self.image_name).group(2)

class EnvironmentParser(object):
    DEFAULT_NAMESPACE = 'default'

    def __init__(self, target_namespace):
        self.target_env = os.environ.get('TARGET_ENV');
        self.target_namespace = target_namespace
        if target_namespace == '':
            self.target_namespace = self.DEFAULT_NAMESPACE;
        self._env = "{0}:{1}".format(self.target_env,self.target_namespace )

    def namespace(self):
        return self.target_namespace

    def name(self):
        return self.target_env

    def env(self):
        return self._env

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

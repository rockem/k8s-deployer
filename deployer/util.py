import os
import re

from kubectlconf.sync import S3ConfSync


class ImageNameParser(object):
    SERVICE_NAME_PATTERN = r'^(.*/)?(.+):'

    def __init__(self, image_name):
        self.image_name = image_name

    def name(self):
        return re.search(self.SERVICE_NAME_PATTERN, self.image_name).group(2)


class EnvironmentParser(object):
    DEFAULT_NAMESPACE = 'default'

    def __init__(self, env):
        self.env = env.split(':', 1)
        if self.__no_namespace_in(self.env):
            self.env.append(self.DEFAULT_NAMESPACE)

    def __no_namespace_in(self, env):
        return len(env) < 2

    def namespace(self):
        return self.env[1]

    def env_name(self):
        return self.env[0]


def update_kubectl(env):
    pass
    # S3ConfSync(EnvironmentParser(env).env_name()).sync()


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

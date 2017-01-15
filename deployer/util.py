import re


class ImageNameParser(object):

    SERVICE_NAME_PATTERN = r'^(.*/)?(.+):'

    def __init__(self, image_name):
        self.image_name = image_name

    def name(self):
        return re.search(self.SERVICE_NAME_PATTERN, self.image_name).group(2)


class EnvironmentParser(object):
    def __init__(self, env):
        self.env = env

    def get_env_namespace(self):
        if ':' not in self.env:
            return 'default'
        return self.env.split(':', 1)[1]

    def get_env_name(self):
        if ':' not in self.env:
            return self.env
        return self.env.split(':', 1)[0]

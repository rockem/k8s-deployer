import subprocess

import os
import yaml

from deployer.util import EnvironmentVariablesFetcher
from log import DeployerLogger

logger = DeployerLogger('yml').getLogger()


class NodeNotFoundError(Exception):
    def __init(self, message):
        super(NodeNotFoundError, self).__init__(message)


class YmlCreator(object):
    def __init__(self, base_yml):
        self.base_yml = base_yml
        self.configuration = {}
        self.nodes = []

    def config(self, properties):
        self.configuration.update(properties)
        return self

    def append(self, element, location):
        self.nodes.append({'yml': element, 'locator': ByPath(location), 'config': {}})
        return self

    def create(self):
        data = yaml.load(self.__apply_configuration(self.base_yml))
        for node in self.nodes:
            config = node['config']
            node['locator'].locate(data).append(yaml.load(self.__apply_configuration(node['yml'], config)))
        return yaml.dump(data, default_flow_style=False)

    def __apply_configuration(self, lines, config={}):
        try:
            lines = lines.format(**config)
        except KeyError:
            pass
        return lines.format(**self.configuration)

    def append_many(self, node, locator, config):
        for c in config:
            self.nodes.append({'yml': node, 'locator': locator, 'config': c})
        return self


def find_node(location, root):
    output = root
    if location is not None:
        for p in location.split('.'):
            try:
                output = output[p]
            except:
                raise NodeNotFoundError("No element on location : %s " % location)
    return output


class ByPath:
    def __init__(self, path):
        self.path = path

    def locate(self, data):
        return find_node(self.path, data)


class SwaggerFileReader(object):

    def __init__(self,swagger_yml_path):
        self.sw_yml_path = swagger_yml_path

    def read(self):
        return subprocess.check_output(" curl -H 'Authorization: token '" + EnvironmentVariablesFetcher().fetch("TOKEN_ID")+ " " + self.sw_yml_path, shell=True)




class FileYmlCreator:
    def __init__(self, yml_dir, base_yml):
        self.yml_dir = yml_dir
        self.base_yml = base_yml
        self.__creator = YmlCreator(self.__read(self.__yml_path(base_yml)))

    def __read(self, path):
        with open(path, 'r') as f:
            return f.read()

    def __yml_path(self, template, path=None):
        if path is None:
            path = self.yml_dir
        return os.path.join(path, template) + '.yml'

    def config(self, properties):
        self.__creator.config(properties)
        return self

    def append(self, yml_path, location):
        self.__creator.append(self.__read(self.__yml_path(yml_path)), location)
        return self

    def create(self, out_dir):
        self.__create_if_needed(out_dir)
        yml_path = self.__yml_path(self.base_yml, out_dir)
        with open(yml_path, 'w') as f:
            f.write(self.__creator.create())
        return yml_path

    def __create_if_needed(self, out_dir):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

    def append_many(self, yml_path, locator, config):
        self.__creator.append_many(self.__read(self.__yml_path(yml_path)), locator, config)


class YmlReaderError(Exception):
    def __init__(self, message):
        super(YmlReaderError, self).__init__(message)


class YmlReader(object):
    def __init__(self, path_or_content):
        self.path_or_content = path_or_content

    def read(self):
        try:
            content = open(self.path_or_content, "r")
            return yaml.load(content)
        except IOError as err:
            logger.warn("Could not load yml path '%s' with the error: '%s'. Will try to read it as a raw string." % (self.path_or_content, err.strerror))
            if self.path_or_content != '':
                return yaml.load(self.path_or_content)
            else:
                return {}

    def read_lines(self):
        with open(str(self.path_or_content), "r+") as f:
            return f.read()

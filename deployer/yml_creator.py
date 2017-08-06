import os

import yaml

from file import YamlReader, YamlWriter


class K8sYmlLocationError(Exception):
    def __init(self, message):
        super(K8sYmlLocationError, self).__init__(message)

class K8sYmlCreator(object):

    def __init__(self,source_dir='./deployer/orig/', dest_dir='./out/'):
        self.source_dir = source_dir
        self.dest_dir = dest_dir

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

    def generate(self,configuration,target):
        self.target = target
        self.configuration = configuration
        self.__generate(self.target)
        return self

    def __generate(self, target):
        lines = YamlReader.read_lines(self.__full_path(self.source_dir, target), "r")
        data = self.__find_and_replace_configuration(lines)
        YamlWriter.write_lines(self.__full_path(self.dest_dir, target), data)

    def __full_path(self, path, element):
        return path + element + ".yml"

    def append_node(self, element, location = None):
        if self.configuration.has_key(element) and self.configuration[element]!='NONE':
            self.__generate(element)
            dict= YamlReader.read(self.__full_path(self.dest_dir,  self.target))
            node = self.__find_node(location, dict)
            node.append(YamlReader.read(self.__full_path(self.dest_dir, element)))
            with open(self.__full_path(self.dest_dir, self.target), "w+") as f:
                yaml.dump(dict, f, default_flow_style=False)
        return self

    def __find_node(self, location, dict):
        output = dict
        if location != None:
            for p in location.split('.'):
                try:
                    output = output[p]
                except:
                    raise K8sYmlLocationError("No element on location : %s " % location)
        return output


    def __find_and_replace_configuration(self, lines):
        return lines.format(**self.configuration)


    def full_path(self):
        return self.__full_path(self.dest_dir, self.target)

import os

from file import YamlReader, YamlWriter


class YmlLocationError(Exception):
    def __init(self, message):
        super(YmlLocationError, self).__init__(message)


SOURCE_DIR = './orig/'
DEST_DIR = './out/'


class YmlCreator(object):
    def __init__(self, configuration, target):
        if not os.path.exists(DEST_DIR):
            os.makedirs(DEST_DIR)
        self.target = target
        self.configuration = configuration
        self.__generate(self.target)

    def __generate(self, target):
        lines = YamlReader(self.__full_path(SOURCE_DIR, target)).read_lines()
        data = self.__find_and_replace_configuration(lines)
        YamlWriter(self.__full_path(DEST_DIR, target)).write_lines(data)

    def __full_path(self, path, element):
        return path + element + ".yml"

    def append_node(self, element, location=None):
        self.__generate(element)
        data = YamlReader(self.__full_path(DEST_DIR, self.target)).read()
        self.__retrieve_node(location, data).append(YamlReader(self.__full_path(DEST_DIR, element)).read())
        YamlWriter(self.__full_path(DEST_DIR, self.target)).update(data)
        return self

    def __retrieve_node(self, location, root):
        output = root
        if location is not None:
            for p in location.split('.'):
                try:
                    output = output[p]
                except:
                    raise YmlLocationError("No element on location : %s " % location)
        return output

    def __find_and_replace_configuration(self, lines):
        return lines.format(**self.configuration)

    def create(self):
        return self.__full_path(DEST_DIR, self.target)

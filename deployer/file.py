import yaml

from log import DeployerLogger

logger = DeployerLogger('YamlReader').getLogger()


class YamlReader(object):
    def __init__(self, path):
        self.path = path

    def read(self):
        try:
            content = open(str(self.path), "r+")
            return yaml.load(content)
        except IOError as err:
            logger.warn("Could not load yml path '%s' with the error: '%s'. Will try to read it as a raw string." % (
                self.path, err.strerror))
            if self.path != '':
                return yaml.load(self.path)
            else:
                return {}

    def read_lines(self):
        with open(str(self.path), "r+") as f:
            return f.read()

    def read_yaml_from_raw_string(self):
        if len(self.path) == 0:
            return {}
        try:
            dictionary = dict(x.split(':') for x in self.path.split(';'))
            return self.convert_bool_representations_to_bool_types(dictionary)
        except ValueError as error:
            logger.warn("Could not parse string '%s' with the error: '%s'. Will return empty dictionary." % (self.path, error.message))
            return {}

    @staticmethod
    def convert_bool_representations_to_bool_types(dictionary):
        for key, value in dictionary.items():
            if value.lower() == "true":
                dictionary[key] = True
            if value.lower() == "false":
                dictionary[key] = False
        return dictionary

class YamlWriter(object):
    def __init__(self, path):
        self.path = path

    def write_lines(self, lines):
        f = open(str(self.path), "w")
        for line in lines:
            f.write(line)
        f.close()

    def update(self, data):
        with open(self.path, "w+") as f:
            yaml.dump(data, f, default_flow_style=False)

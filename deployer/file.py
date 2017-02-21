import yaml


class YamlReader(object):

    def read(self, path):
        try:
            content = open(str(path), "r+")
            return yaml.load(content)
        except IOError:
            return {}
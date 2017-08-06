import yaml


class YamlReader(object):

    @staticmethod
    def read( path):
        try:
            content = open(str(path), "r+")
            return yaml.load(content)
        except IOError:
            return {}
    @staticmethod
    def read_lines(path, rw):
        with open(str(path), rw) as f:
            return f.read()


class YamlWriter(object):
    @staticmethod
    def write_lines( path, lines):
        f = open(str(path), "w")
        for line in lines:
            f.write(line)
        f.close()


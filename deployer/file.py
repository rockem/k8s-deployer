import yaml


class YamlReader(object):

    def read(self, path):
        try:
            content = open(str(path), "r+")
            return yaml.load(content)
        except IOError:
            return {}
    def read_lines(self, path, rw):
        with open(str(path), rw) as f:
            return f.read()


class YamlWriter(object):

    def write_lines(self, path, lines):
        f = open(str(path), "w")
        for line in lines:
            f.write(line)
        f.close()


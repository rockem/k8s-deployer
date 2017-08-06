import yaml


class YamlReader(object):
    def __init__(self,path):
        self.path=path

    def read(self):
        try:
            content = open(str(self.path), "r+")
            return yaml.load(content)
        except IOError:
            return {}

    def read_lines(self,):
        with open(str(self.path),  "r+") as f:
            return f.read()


class YamlWriter(object):
    def __init__(self,path):
        self.path=path

    def write_lines(self, lines):
        f = open(str(self.path), "w")
        for line in lines:
            f.write(line)
        f.close()

    def update(self, data):
        with open(self.path, "w+") as f:
            yaml.dump(data, f, default_flow_style=False)
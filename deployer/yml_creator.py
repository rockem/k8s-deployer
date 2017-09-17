import yaml


class YmlLocationError(Exception):
    def __init(self, message):
        super(YmlLocationError, self).__init__(message)


class YmlCreator(object):
    def __init__(self, base_yml):
        self.base_yml = base_yml
        self.configuration = {}
        self.nodes = {}

    def config(self, properties):
        self.configuration.update(properties)
        return self

    def append_node(self, element, location):
        self.nodes[location] = element
        return self

    def create(self):
        data = yaml.load(self.__apply_configuration(self.base_yml))
        for location, element in self.nodes.iteritems():
            self.__retrieve_node(location, data).append(yaml.load(self.__apply_configuration(element)))
        return yaml.dump(data, default_flow_style=False)

    def __retrieve_node(self, location, root):
        output = root
        if location is not None:
            for p in location.split('.'):
                try:
                    output = output[p]
                except:
                    raise YmlLocationError("No element on location : %s " % location)
        return output

    def __apply_configuration(self, lines):
        return lines.format(**self.configuration)

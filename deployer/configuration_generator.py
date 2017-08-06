import os

import yaml

from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class TemplateCorruptedError(Exception):
    def __init(self, message):
        super(TemplateCorruptedError, self).__init__(message)

# class ConfigAppender(object):
#
#     def __init__(self, element):
#         self.config = yaml.load(open(get_target_dest(element)))
#
#     def append_to(self, target):
#         deployment = yaml.load(open(get_target_dest(target)))
#         deployment['spec']['template']['spec']['containers'].append(self.config)
#         self.__write_to_target(deployment, target)
#         logger.debug(" logging append succeeded for %s" % target)
#
#     def __write_to_target(self, deployment, target):
#         with open(get_target_dest(target), "w+") as f:
#             yaml.dump(deployment, f, default_flow_style=False)

class ConfigGenerator(object):
    def __init__(self, service_configuration):
        self.service_configuration = service_configuration
        if not os.path.exists("deployer/produce/"):
            os.makedirs("deployer/produce/")

    def generate(self, target):
        self.target = target
        f = self.__open_file_for(self.target, "w+")
        f.close()
        return self

    def by_template(self, source):
        lines = self.__read_lines_from_source(source)
        f = self.__open_file_for(self.target, "w+")
        logger.debug("match and replace service properties values @ %s" % self.target)
        self.__write_to_target(f, self.__find_and_replace_service_configuration(lines))
        logger.debug("%s generation succeeded" % self.target)

    def __open_file_for(self, path, rw):
        f = open(str(path), rw)
        return f

    def __find_and_replace_service_configuration(self, lines):
        try:
            return lines.format(**self.service_configuration)
        except KeyError as e:
            raise TemplateCorruptedError(
                "template corrupted - we found properties in template that is missing in the configuration!:  " + e.message)

    def __read_lines_from_source(self, source):
        with self.__open_file_for(source, "r") as f:
            return f.read()

    def __write_to_target(self, f, new_lines):
        for line in new_lines:
            f.write(line)
        f.close()

import os
import re

from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


class TemplateCorruptedError(Exception):
    def __init(self, message):
        super(TemplateCorruptedError, self).__init__(message)


class ConfigurationGenerator(object):
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
        self.__validate_configuration_properties_against_template(lines)
        new_lines = []
        f = self.__open_file_for(self.target, "w+")
        self.__validate_service_configuration(f, lines)
        logger.debug("match and replace service properties values @ %s" % self.target)
        self.__find_and_replace_service_configuration(lines, new_lines)
        self.__write_to_target(f, new_lines)
        logger.debug("%s generation succeeded" % self.target)

    def __validate_configuration_properties_against_template(self, lines):
        params = re.findall(r"\{([.A-Za-z0-9_]+)\}", str(lines))
        if params:
            keys = self.service_configuration.keys()
            if set(params) - set(keys):
                logger.warning((
                               "template corrupted - we found properties in configuration that is missing in the template!:  " + str(
                                   set(keys) - set(params))))
                raise TemplateCorruptedError(
                    "template corrupted - we found properties in configuration that is missing in the template!:  " + str(
                        set(keys) - set(params)))

    def __open_file_for(self, path, rw):
        f = open(str(path), rw)
        return f

    def __find_and_replace_service_configuration(self, lines, new_lines):
        for line in lines:
            new_line = line
            # maybe not the best performance but readable and working
            for key in self.service_configuration:
                new_line = new_line.replace("{" + key + "}", self.service_configuration[key])
            new_lines.append(new_line)

    def __validate_service_configuration(self, f, lines):
        if not self.service_configuration:
            self.__write_to_target(f, lines)

    def __read_lines_from_source(self, source):
        f = self.__open_file_for(source, "r")
        lines = []
        for line in f.readlines():
            lines.append(line)
        f.close()
        return lines

    def __write_to_target(self, f, new_lines):
        for line in new_lines:
            f.write(line)
        f.close()

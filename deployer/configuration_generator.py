import os
import re

from deployerLogger import DeployerLogger

logger = DeployerLogger(__name__).getLogger()

class TemplateCorruptedError(Exception):

    def __init(self, message):
        super(TemplateCorruptedError, self).__init__(message)

class ConfigurationGenerator(object):

    def __init__(self, serviceConfiguration):
        self.serviceConfiguration = serviceConfiguration
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
        newLines = []
        f = self.__open_file_for(self.target, "w+")
        self.__validate_service_configuration(f, lines)
        logger.debug("match and replace service properties values @ %s" %(self.target))
        self.__find_and_replace_service_configuration(lines, newLines)
        self.__write_to_target(f, newLines)
        logger.debug("%s generation succeeded" %(self.target))

    def __validate_configuration_properties_against_template(self, lines):
        params = re.findall(r"\{([\.A-Za-z0-9_]+)\}", str(lines))
        if params:
            keys =  self.serviceConfiguration.keys()
            if set(params) - set(keys):
                logger.warning(("template corrupted - we found properties in configuration that is missing in the template!:  " + str(set(keys) - set(params))))
                raise TemplateCorruptedError("template corrupted - we found properties in configuration that is missing in the template!:  " + str(set(keys) - set(params)))

    def __open_file_for(self, path, rw):
        f = open(str(path), rw)
        return f

    def __find_and_replace_service_configuration(self, lines, newLines):
        for line in lines:
            key = re.search(r"\{([\.A-Za-z0-9_]+)\}", str(line))
            if key:
                v = dict(self.serviceConfiguration).get(str(key.group(1)))
                newLines.append(line.replace("{" + str(key.group(1))+ "}", str(v)))
            else:
                if line not in newLines:
                    newLines.append(line)

    def __validate_service_configuration(self, f, lines):
        if not self.serviceConfiguration:
            self.__write_to_target(f, lines)

    def __read_lines_from_source(self, source):
        f = self.__open_file_for(source, "r")
        lines = []
        for line in f.readlines():
            lines.append(line)
        f.close()
        return lines

    def __write_to_target(self, f, newLines):
        for line in newLines:
            f.write(line)
        f.close()
import yaml

from configuration_generator import ConfigurationGenerator
from k8sDeployer import K8sDeployer
from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()



class LoggerConfigAppender(object):

    def __init__(self, element):
        self.config = yaml.load(open(get_target_dest(element)))

    def append_to(self, target):
        deployment = yaml.load(open(get_target_dest(target)))
        deployment['spec']['template']['spec']['containers'].append(self.config)
        self.__write_to_target(deployment, target)
        logger.debug(" logging append succeeded for %s" % target)

    def __write_to_target(self, deployment, target):
        with open(get_target_dest(target), "w+") as f:
            yaml.dump(deployment, f, default_flow_style=False)


class DeployRunner(object):
    def __init__(self, connector):
        self.connector = connector

    def deploy(self, configuration, elements):
        for element in elements:
            logger.debug("element : {}".format(element))
            self.__generate_element(configuration, str(element))
            self.__append_log(configuration, element)
            K8sDeployer(self.connector).deploy('%s.yml' % element).to()

    def __append_log(self, configuration, element):
        logging_elem = 'logging'
        if str(element) == 'deployment' and configuration.has_key(logging_elem) and configuration[logging_elem] != 'NONE':
            self.__generate_element(configuration, logging_elem)
            LoggerConfigAppender(logging_elem).append_to(element)

    def __generate_element(self,configuration, element):
         ConfigurationGenerator(configuration).generate(get_target_dest(element)).by_template(
            get_source_dest(element))


def get_source_dest(element):
    return 'deployer/orig/%s.yml' % element


def get_target_dest(element):
    return 'deployer/produce/%s.yml' % element


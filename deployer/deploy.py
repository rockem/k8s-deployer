import time

from color_desider import ColorDesider
from deployRunner import DeployRunner
from k8s import PodHealthChecker, ServiceExplorer
from log import DeployerLogger
from util import ImageNameParser

logger = DeployerLogger('ImageDeployer').getLogger()


class DeployError(Exception):
    def __init(self, message):
        super(DeployError, self).__init__(message)


class ImageDeployer(object):
    def __init__(self, image, target, connector):
        self.image = image
        self.target = target
        self.configuration = {}
        self.connector = connector
        self.deploy_runner = DeployRunner(connector)
        self.health_checker = PodHealthChecker(connector)

    def deploy(self):
        self.__dark_deploy()  # create config
        if self.__is_healthy():
            logger.debug ("Lets expose this MF %s" % self.image)
            self.__expose()
        else:
            raise DeployError('deploy %s failed!' % self.image)

    def __dark_deploy(self):
        self.configuration = self.__create_props()
        print "going to dark deploy with this config {}".format(self.configuration)
        self.deploy_runner.deploy(self.configuration, ['deployment', 'service'])

    def __is_healthy(self):
        name = "%s" % self.configuration["name"]
        logger.debug("this is a name ->>>>>>>>> %s" % name)
        return self.__busy_wait(self.health_checker.health_check, name)  # TODO - use name not concat

    def __busy_wait(self, run_func, *args):
        result = False
        for _ in range(10):  # TODO - should be 120
            logger.debug ('try # %s' % _)
            try:
                if run_func(args[0]):
                    result = True
                    break
            except Exception:
                pass
            time.sleep(1)

        logger.debug ("BW=> %s" % result)
        return result

    def __expose(self):
        self.configuration['serviceColor'] = ColorDesider().invert_color(self.configuration.get("serviceColor"))
        self.deploy_runner.deploy(self.configuration, ['service'])

    def __create_props(self):
        name = ImageNameParser(self.image).name()
        color = ServiceExplorer(self.connector).get_color(name)
        # pod_color = ColorDesider().invert_color(color)
        # logger.debug('this is the pod color %s' % pod_color)
        return {
            'env': self.target,
            'name': name + "-" + ColorDesider().invert_color(color),
            'serviceName' : name,
            'image': self.image,
            'podColor': ColorDesider().invert_color(color),
            'serviceColor': color
        }

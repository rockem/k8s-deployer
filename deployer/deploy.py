import time

from color_desider import ColorDesider
from deployRunner import DeployRunner
from k8s import PodHealthChecker, ServiceExplorer
from log import DeployerLogger
from util import ImageNameParser, EnvironmentParser

logger = DeployerLogger('ImageDeployer').getLogger()


class DeployError(Exception):
    def __init(self, message):
        super(DeployError, self).__init__(message)


class ImageDeployer(object):
    def __init__(self, target, connector, recipe, timeout):
        self.target = target
        self.configuration = {}
        self.connector = connector
        self.deploy_runner = DeployRunner(connector)
        self.health_checker = PodHealthChecker(connector)
        self.recipe = recipe
        self.timeout = timeout

    def deploy(self):
        if not self.__exposed():
            self.__deploy()
        else:
            self.__blue_green_deploy()

    def __blue_green_deploy(self):
        self.__dark_deploy()  # create config
        if self.__is_healthy():
            logger.debug("Lets expose this MF %s" % self.recipe.image())
            self.__expose()
        else:
            raise DeployError('deploy %s failed!' % self.recipe.image)

    def __exposed(self):
        logger.debug("recipe path is %s" % self.recipe)
        return self.recipe.expose()

    def __deploy(self):
        self.configuration = self.__create_props_force()
        print "going to force deploy with this config {}".format(self.configuration)
        self.deploy_runner.deploy(self.configuration, ['deployment'])

    def __dark_deploy(self):
        self.configuration = self.__create_props_blue_green()
        print "going to dark deploy with this config {}".format(self.configuration)
        self.deploy_runner.deploy(self.configuration, ['deployment', 'service'])

    def __is_healthy(self):
        name = "%s" % self.configuration["name"]
        logger.debug("this is a name ->>>>>>>>> %s" % name)
        return self.__busy_wait(self.health_checker.health_check, name)  # TODO - use name not concat

    def __busy_wait(self, run_func, *args):
        result = False
        for _ in range(self.timeout):
            logger.debug('try # %s' % _)
            try:
                if run_func(args[0]):
                    result = True
                    break
            except Exception:
                pass
            time.sleep(1)

        logger.debug("BW=> %s" % result)
        return result

    def __expose(self):
        self.configuration['serviceColor'] = ColorDesider().invert_color(self.configuration.get("serviceColor"))
        self.deploy_runner.deploy(self.configuration, ['service'])

    def __create_props_blue_green(self):
        name = ImageNameParser(self.recipe.image()).name()
        print "Name is: %s" % name
        color = ServiceExplorer(self.connector).get_color(name)
        return {
            'env': self.target,
            'name': name + "-" + ColorDesider().invert_color(color),
            'serviceName': name,
            'image': self.recipe.image(),
            'podColor': ColorDesider().invert_color(color),
            'serviceColor': color,
            'myEnv': EnvironmentParser(self.target).env_name()
        }

    def __create_props_force(self):
        name = ImageNameParser(self.recipe.image()).name()
        color = ServiceExplorer(self.connector).get_color(name)
        return {
            'env': self.target,
            'name': name,
            'serviceName': name,
            'image': self.recipe.image(),
            'podColor': ColorDesider().invert_color(color),
            'serviceColor': color,
            'myEnv': EnvironmentParser(self.target).env_name()
        }

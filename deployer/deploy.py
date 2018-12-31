from __future__ import print_function
import time

from k8s import PodHealthChecker, AppExplorer
from log import DeployerLogger
from util import ImageNameParser, EnvironmentParser

logger = DeployerLogger('ImageDeployer').getLogger()


class DeployError(Exception):
    def __init(self, message):
        super(DeployError, self).__init__(message)


class ColorDecider(object):
    COLORS = {
        'blue': 'green',
        'green': 'blue'
    }

    def invert_color(self, color):
        return self.COLORS[color]

    def default_color(self):
        return 'blue'


class ImageDeployer(object):
    def __init__(self, args, connector, recipe):
        self.target = args["target"]
        self.domain = args["domain"]
        self.configuration = {}
        self.connector = connector
        self.health_checker = PodHealthChecker(connector)
        self.recipe = recipe
        self.timeout = args["deploy_timeout"]
        self.force = args["force"]

    def deploy(self):
        if not self.__exposed() or self.force:
            self.__deploy()
        else:
            self.__blue_green_deploy()

    def __exposed(self):
        logger.debug("recipe path is %s" % self.recipe)
        return self.recipe.expose()

    def __deploy(self):
        self.configuration = self.__create_props(True)
        self.connector.apply_service_account(self.configuration)
        self.connector.apply_deployment(self.configuration)
        print("going to force deploy with this config {}".format(self.configuration))

    def __create_props(self, force):
        name = ImageNameParser(self.recipe.image()).name()
        color = AppExplorer(self.connector).get_color(name)
        scale = AppExplorer(self.connector).get_deployment_scale(name)
        invert_color = ColorDecider().invert_color(color)
        return {
            'env': EnvironmentParser(self.target).env(),
            'name': name if force else name + "-" + invert_color,
            'scale': scale,
            'serviceName': name,
            'image': self.recipe.image(),
            'podColor': invert_color,
            'serviceColor': color,
            'myEnv': EnvironmentParser(self.target).name(),
            'logging': self.recipe.logging(),
            'ports': self.recipe.ports(),
            'domain': self.domain,
            'serviceType': self.recipe.service_type(),
            'target': EnvironmentParser(self.target).namespace(),
            'metrics': self.recipe.metrics()
        }

    def __blue_green_deploy(self):
        self.__dark_deploy()  # create config
        if self.__is_healthy():
            logger.debug("Lets force expose this MF %s" % self.recipe.image())
            self.__expose()
        else:
            self.__revert_bad_deploy()
            raise DeployError('Deploy %s failed! Health check failed. pod description : %s' % (self.recipe.image(),
                                                                                               self.health_checker.connector.describe_pod(
                                                                                                   self.configuration[
                                                                                                       "name"])))

    def __dark_deploy(self):
        self.configuration = self.__create_props(False)
        print("going to dark deploy with this config {}".format(self.configuration))
        self.connector.apply_service_account(self.configuration)
        self.connector.apply_deployment(self.configuration)
        self.connector.apply_service(self.configuration)

    def __revert_bad_deploy(self):
        color = ColorDecider().invert_color(self.configuration.get("serviceColor"))
        self.__scale_deployment_with_color(color, 0)

    def __is_healthy(self):
        name = "%s" % self.configuration["name"]
        print("Waiting for %s to be healthy..." % name)
        return self.__busy_wait(self.health_checker.health_check, name)

    def __busy_wait(self, run_func, *args):
        result = False
        for _ in range(self.timeout):
            print('.', end='')
            try:
                if run_func(args[0]):
                    result = True
                    break
            except Exception:
                pass
            time.sleep(1)
        return result

    def __expose(self):
        color = self.configuration.get("serviceColor")
        self.configuration['serviceColor'] = ColorDecider().invert_color(color)
        self.connector.apply_service(self.configuration)
        self.__scale_deployment_with_color(color, 0)

    def __scale_deployment_with_color(self, color, new_scale):
        name = ImageNameParser(self.recipe.image()).name()
        self.connector.scale_deployment(name + '-' + color, new_scale)

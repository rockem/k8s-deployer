import sys
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

    def __init__(self, image, target):
        self.image = image
        self.target = target
        self.configuration = {}

    def deploy(self):
        self.__dark_deploy() # create config
        if self.__is_healthy():
            print "Lets expose this MF %s" % self.image
            self.__expose()
        # else:
        #     raise DeployError('deploy %s failed!' %self.image)

    def __dark_deploy(self):
        self.configuration = self.__create_props()
        DeployRunner(self.configuration).deploy(['deployment', 'service'])

    def __is_healthy(self):
        return self.__busy_wait(PodHealthChecker("%s-%s" %(self.configuration["name"], self.configuration["podColor"])).health_check) #TODO - use name not concat

    def __busy_wait(self,run_func):
        result = False
        for _ in range(10): #TODO - should be 120
            print 'try # %s' %_
            try:
                if run_func():
                    result = True
                    break
            except Exception:
                pass
            time.sleep(1)

        print "BW=> %s" % result
        return result

    def __expose(self):
        self.configuration['serviceColor'] = ColorDesider().invert_color(self.configuration.get("serviceColor"))
        DeployRunner(self.configuration).deploy(['service'])

    def __create_props(self):
        name = ImageNameParser(self.image).name()
        color = ServiceExplorer(name).get_color()
        return {
            'env': self.target,
            'name': name,
            'image': self.image,
            'podColor' : ColorDesider().invert_color(color),
            'serviceColor' : color
        }
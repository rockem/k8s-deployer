import re
import subprocess
import sys
import time

from flask import json

from color_desider import ColorDesider
from deployRunner import DeployRunner
from k8s import PodHealthChecker
from k8sConfig import k8sConfig
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
        self.deploy_run = DeployRunner()

    def deploy(self):
        self.__dark_deploy() # create config
        if self.__is_healthy():
            print "Lets expose this MF %s" % self.image
            self.__expose()
        # else:
        #     raise DeployError('deploy %s failed!' %self.image)

    def __dark_deploy(self):
        self.configuration = self.__create_props()
        self.deploy_run.deploy(k8sConfig().by(self.configuration))

    def __is_healthy(self):
        return self.__busy_wait(PodHealthChecker(self.__extract_pod_name("%s-%s" %(self.configuration["name"], self.configuration["podColor"]))).health_check)

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
        self.__change_service_color_to()
        self.deploy_run.deploy(k8sConfig().service_by(self.configuration))

    # def __expose_pod(self):
    #     counter = 0
    #     while counter < 5: #TODO - should be 120
    #         counter = counter +1
    #         try:
    #             if self.__pod_is_healthy():
    #                 self.__change_service_color_to()
    #                 self.deploy_run.deploy(k8sConfig().service_by(self.configuration))
    #                 break
    #             else:
    #                 self.__sleep_for(1)
    #         except Exception as e:
    #             self.__sleep_for(1)

    def __sleep_for(self, sec):
        time.sleep(sec)

    def __change_service_color_to(self):
        self.configuration['serviceColor'] = ColorDesider().invert_color(self.configuration.get("serviceColor"))

    def __extract_pod_name(self, service_name):
        output = subprocess.check_output("kubectl describe pods %s" % service_name, shell=True, stderr=subprocess.STDOUT)
        match = re.search(r"Name:\s(.*)", output)
        if match:
            return match.group(1)
        else:
            raise Exception('service %s has no pod!' % service_name)
    #
    # def __pod_is_healthy(self):
    #     pod_name = self.__extract_pod_name("%s-%s" %(self.configuration["name"], self.configuration["podColor"]))
    #     print 'working on %s' %pod_name
    #     subprocess.check_output("kubectl exec -p %s wget http://localhost:5000/health" % pod_name, shell=True, stderr=subprocess.STDOUT)
    #     output = subprocess.check_output("kubectl exec -p %s cat health" % pod_name, shell=True, stderr=subprocess.STDOUT)
    #     print 'pod health output %s' %output
    #     self.__cleanup_pod(pod_name)
    #     return 'UP' in output #parse as json
    #
    # def __cleanup_pod(self, pod_name):
    #     try:
    #         subprocess.check_output("kubectl exec -p %s rm health" % pod_name, shell=True, stderr=subprocess.STDOUT)
    #     except subprocess.CalledProcessError as e:
    #         logger.debug('health was cleaned for %s, nothing to delete here' % pod_name)

    def __create_props(self):
        name = ImageNameParser(self.image).name()
        color = self.__calc_service_color(name)
        return {
            'env': self.target,
            'name': name,
            'image': self.image,
            'podColor' : ColorDesider().invert_color(color),
            'serviceColor' : color
        }

    def __validate_image_contains_tag(self):
        if ':' not in self.image:
            logger.error('image_name should contain the tag')
            sys.exit(1)

    def __calc_service_color(self, name, DEFAULT_COLOR='blue'):
        try:
            output = subprocess.check_output("kubectl get svc %s -o json" % name, shell=True, stderr=subprocess.STDOUT)
            print 'we found a version of %s, its color is %s' %(name, json.loads(output)['spec']['selector']['color'])
            return json.loads(output)['spec']['selector']['color']
        except subprocess.CalledProcessError as e:
            if e.returncode is not 0:
                print 'this is the first time this service is been deployed! this is the color %s' %DEFAULT_COLOR
                return DEFAULT_COLOR
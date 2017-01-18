import re
import subprocess

from flask import json

from log import DeployerLogger

logger = DeployerLogger('PodHealthChecker').getLogger()

class PodHealthChecker(object):

    def health_check(self, pod_name):
        pod_name = self.__extract_pod_name(pod_name)
        print 'working on %s' % pod_name
        subprocess.check_output("kubectl exec -p %s wget http://localhost:8080/health" % pod_name, shell=True, stderr=subprocess.STDOUT)
        output = subprocess.check_output("kubectl exec -p %s cat health" % pod_name, shell=True, stderr=subprocess.STDOUT)
        print 'pod health output %s' %output
        self.__cleanup_pod(pod_name)
        return 'UP' in output #parse as json

    def __cleanup_pod(self, pod_name):
        try:
            subprocess.check_output("kubectl exec -p %s rm health" % pod_name, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logger.debug('health was cleaned for %s, nothing to delete here' % pod_name)

    def __extract_pod_name(self, pod_name):
        output = subprocess.check_output("kubectl describe pods %s" % pod_name, shell=True, stderr=subprocess.STDOUT)
        match = re.search(r"Name:\s(.*)", output)
        if match:
            return match.group(1)
        else:
            raise Exception('service %s has no pod!' % pod_name)



class ServiceExplorer(object):

    def __init__(self, service_name):
        self.service_name = service_name

    def get_color(self, default_color='blue'):
        try:
            output = subprocess.check_output("kubectl get svc %s -o json" %  self.service_name, shell=True, stderr=subprocess.STDOUT)
            return json.loads(output)['spec']['selector']['color']
        except subprocess.CalledProcessError as e:
            if e.returncode is not 0:
                return default_color

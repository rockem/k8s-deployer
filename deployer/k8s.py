import re
import subprocess

from flask import json

from log import DeployerLogger

logger = DeployerLogger('PodHealthChecker').getLogger()

class PodHealthChecker(object):

    def __init__(self, pod_name):
        self.pod_name = self.__extract_pod_name(pod_name)

    def health_check(self):
        print 'working on %s' % self.pod_name
        subprocess.check_output("kubectl exec -p %s wget http://localhost:5000/health" % self.pod_name, shell=True, stderr=subprocess.STDOUT)
        output = subprocess.check_output("kubectl exec -p %s cat health" % self.pod_name, shell=True, stderr=subprocess.STDOUT)
        print 'pod health output %s' %output
        self.__cleanup_pod()
        return 'UP' in output #parse as json

    def __cleanup_pod(self):
        try:
            subprocess.check_output("kubectl exec -p %s rm health" % self.pod_name, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logger.debug('health was cleaned for %s, nothing to delete here' % self.pod_name)

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

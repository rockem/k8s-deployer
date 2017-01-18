import subprocess

from log import DeployerLogger

logger = DeployerLogger('PodHealthChecker').getLogger()

class PodHealthChecker(object):

    def __init__(self, pod_name):
        self.pod_name = pod_name

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
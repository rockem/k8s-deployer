import os
import re

import subprocess
from subprocess import CalledProcessError

from flask import json


class TestDeployCommand:

    #healthy-agur-1484242029
    def test_service_color_should_be_default(self):
        assert self.__calc_service_color('test', 'green') == 'green'

    def test_service_color_should_be_blue(self):
        assert self.__calc_service_color('healthy-agur-1484242029', 'green') == 'blue'


    def test_validate_pods_status(self):
        pod_name = self.__extract_pods_name('healthy-agur-1484242029')
        self.__cleanup_pod(pod_name)
        self.__call_pods_health(pod_name)
        assert self.__is_healthy(pod_name) == 'Down'
        self.__cleanup_pod(pod_name)



    def __calc_service_color(self, name, default):
        try:
            output = subprocess.check_output("kubectl get svc %s -o json" % name, shell=True, stderr=subprocess.STDOUT)
            return json.loads(output)['spec']['selector']['color']
        except CalledProcessError as e:
            if e.returncode is not 0:
                return default

    def __extract_pods_name(self, service_name):
        output = subprocess.check_output("kubectl describe pods %s" % service_name, shell=True, stderr=subprocess.STDOUT)
        match = re.search(r"Name:\s(.*)", output)
        if match:
            return match.group(1)
        else:
            raise Exception('service %s has no pod!' % service_name)

    def __call_pods_health(self, pod_name):
        subprocess.check_output("kubectl exec -p %s wget http://localhost:5000/health" % pod_name, shell=True, stderr=subprocess.STDOUT)

    def __is_healthy(self, pod_name):
        output = subprocess.check_output("kubectl exec -p %s cat health" % pod_name, shell=True, stderr=subprocess.STDOUT)
        if 'Down' in output:
            return 'Down'
        else:
            raise Exception('pod is down')

    def __cleanup_pod(self, pod_name):
        subprocess.check_output("kubectl exec -p %s rm health" % pod_name, shell=True, stderr=subprocess.STDOUT)
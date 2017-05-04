import json
import re
import subprocess

import requests
import time


class K8sDriver:
    def __init__(self, namespace, minikube=None):
        self.namespace = namespace
        self.minikube = minikube

    def get_service_domain_for(self, app):
        service_up = False
        counter = 0
        result = None
        while counter < 20:
            counter += 1
            try:
                output = subprocess.check_output(
                    "kubectl describe --namespace %s services %s" % (self.namespace, app.service_name()), shell=True)
                print (output)
                if self.minikube is None:
                    match = re.search(r"LoadBalancer Ingress:\s(.*)", output)
                else:
                    match = re.search(r"NodePort:\s*<unset>\s*(\d+)/TCP", output)
                if match:
                    result = match.group(1)
                    print ('found a match -> %s' % result)
                    if self.minikube is not None:
                        result = '%s:%s' % (self.minikube, result)
                        o = requests.get('http://' + result + "/health")
                        print ('this is the service output %s' % o)
                        assert json.loads(o.text)['status']['code'] == 'UP', 'Healthy service not serving anymore'
                        # service_up = True
                        return result
                else:
                    print ('didnt found a match, going to sleep and run for another try')
                    time.sleep(1)
            except Exception as e:
                print('%s is not ready yet, going to sleep and run for another try' % app.service_name())
                time.sleep(1)

        raise Exception('The service in k8s probably did not start')

    def verify_app_is_running(self, app):
        assert self.__busy_wait(self.__pod_running, app.service_name())

    def __busy_wait(self, run_func, *args):
        result = False
        for _ in range(20):  # TODO - should be 120
            try:
                if run_func(*args):
                    result = True
                    break
            except Exception:
                pass
            time.sleep(1)

        return result

    def __pod_running(self, image_name):
        pod_name = self.__grab_pod_name(image_name)
        match = re.search(r"Status:\s(.*)", self.__describe_pod(pod_name))
        if match:
            return match.group(1).strip() == 'Running'
        else:
            raise Exception('service %s has no pod!' % pod_name)

    def __describe_pod(self, pod_name):
        return self.__run("kubectl --namespace %s describe pods %s" % (self.namespace, pod_name))

    def __grab_pod_name(self, pod_name):
        output = self.__run("kubectl --namespace %s get pods" % (self.namespace))
        list = output.split()
        for item in list:
            if item.startswith(pod_name):
                return item

    def __run(self, command):
        return subprocess.check_output(command, shell=True)

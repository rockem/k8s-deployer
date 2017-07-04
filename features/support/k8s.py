import json
import re
import subprocess
import requests
import time
import yaml

from features.support.app import AppDriver
from features.support.repository import LocalConfig

GLOBAL_CONFIG_NAME = 'global-config'
CONFIG_FILE_NAME = 'global.yml'


class K8sDriver:
    def __init__(self, namespace, minikube=None):
        self.namespace = namespace
        self.minikube = minikube

    def get_service_domain_for(self, app):
        counter = 0
        while counter < 120:
            counter += 1
            try:
                output = self.__run(
                    "kubectl describe --namespace %s services %s" % (self.namespace, app.service_name()))
                print ("kubectl describe : %s" %output)
                if self.minikube is None:
                    match = re.search(r"LoadBalancer Ingress:\s(.*)", output)
                else:
                    match = re.search(r"NodePort:\s*<unset>\s*(\d+)/TCP", output)
                if match:
                    result = match.group(1)
                    print ('found a match -> %s' % result)
                    if self.minikube is not None:
                        result = '%s:%s' % (self.minikube, result)
                    print ('request %s','http://' + result + "/health")
                    o = requests.get('http://' + result + "/health")
                    print ('this is the service output %s' % o.text)
                    json_health = json.loads(o.text)
                    assert json_health['status'] == 'UP' or json_health['status']['code'] == 'UP'
                    return result
                else:
                    print ('didnt found a match, going to sleep and run for another try')
                    time.sleep(1)
            except Exception as e:
                print('%s is not ready yet, going to sleep and run for another try' % app.service_name())
                time.sleep(1)

        raise Exception('The service in k8s probably did not start')

    def verify_app_is_running(self, app):
        assert AppDriver.busy_wait(self.__pod_running, app.service_name())

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

    def verify_config_is(self, expected_config):
        assert expected_config == self.__get_k8s_config()

    def __get_k8s_config(self):
        k8s_config_map = self.__run(
            "kubectl get configmap %s --namespace=%s -o yaml" % (GLOBAL_CONFIG_NAME, self.namespace))
        return yaml.load(k8s_config_map)['data'][CONFIG_FILE_NAME]

    def delete_namespace(self):
        subprocess.call("kubectl delete namespace %s" % self.namespace, shell=True)

    def create_namespace(self):
        self.__run("kubectl create namespace %s" % self.namespace)

    @classmethod
    def delete_namespaces(cls, namespaces):
        for n in namespaces:
            subprocess.call("kubectl delete namespace %s" % n, shell=True)

    def upload_config(self, config_name):
        subprocess.call("kubectl delete configmap global-config --namespace=%s" % self.namespace, shell=True)
        self.__run("kubectl create configmap global-config --from-file=global.yml=%s --namespace=%s" % (LocalConfig(config_name).get_path(), self.namespace))

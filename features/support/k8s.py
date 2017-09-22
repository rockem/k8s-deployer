import json
import re
import subprocess
import requests
import time
import yaml

from features.support.app import BusyWait
from features.support.repository import LocalConfig

GLOBAL_CONFIG_NAME = 'global-config'
CONFIG_FILE_NAME = 'global.yml'


class K8sDriver:
    def __init__(self, namespace, minikube=None):
        self.namespace = namespace
        self.minikube = minikube

    def get_service_domain_for(self, app, port_name='tcp-80'):
        if self.minikube is None:
            return ServiceDomainFetcher(self.namespace, self.minikube).fetch(app, port_name)
        else:
            return MinikubeServiceDomainFetcher(self.namespace, self.minikube).fetch(app, port_name)

    def verify_app_is_running(self, app):
        BusyWait.execute(self.__pod_running, app.service_name())

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

    def upload_config(self, config_name):
        subprocess.call("kubectl delete configmap global-config --namespace=%s" % self.namespace, shell=True)
        self.__run("kubectl create configmap global-config --from-file=global.yml=%s --namespace=%s" % (
            LocalConfig(config_name).get_path(), self.namespace))

    @staticmethod
    def add_node_label(name, value):
        subprocess.call("kubectl label --overwrite nodes minikube %s=%s" % (name, value), shell=True)


class ServiceDomainFetcher:
    def __init__(self, namespace, minikube=None):
        self.namespace = namespace
        self.minikube = minikube

    def fetch(self, app, port_name):
        return BusyWait.execute(self.__get_service_domain_for, app.service_name(), port_name)

    def __get_service_domain_for(self, service_name, port_name):
        return self.__extract_domain_name(service_name, port_name)

    def __extract_domain_name(self, service_name, port_name):
        svc_json = json.loads(self.__describe_service(service_name))
        ingress = svc_json['status']['loadBalancer']['ingress']
        if len(ingress) > 0:
            return ['%s:%s' % (ingress[0], p['port'])
                    for p in svc_json['spec']['ports']
                    if p['name'] == port_name][0]
        else:
            raise AttributeError('Failed to find domain in: %s' % svc_json)

    def __describe_service(self, service_name):
        return subprocess.check_output("kubectl get --namespace %s service %s -o json" % (self.namespace, service_name),
                                       shell=True)

    def __check_healthy(self, domain):
        o = requests.get('http://' + domain + "/health", timeout=1)
        json_health = json.loads(o.text)
        assert json_health['status'] == 'UP' or json_health['status']['code'] == 'UP'


class MinikubeServiceDomainFetcher:
    def __init__(self, namespace, minikube_ip):
        self.namespace = namespace
        self.minikube = minikube_ip

    def fetch(self, app, port_name):
        return self.__get_service_domain_for(app.service_name(), port_name)

    def __get_service_domain_for(self, service_name, port_name):
        return self.__extract_domain_name(service_name, port_name)

    def __extract_domain_name(self, service_name, port_name):
        output = self.__describe_service(service_name)
        return [
            '%s:%s' % (self.minikube, p['nodePort'])
            for p in json.loads(output)['spec']['ports']
            if p['name'] == port_name][0]

    def __describe_service(self, service_name):
        return subprocess.check_output(
            "kubectl get --namespace %s service %s -o json" % (self.namespace, service_name), shell=True)

    def __check_healthy(self, domain):
        o = requests.get('http://' + domain + "/health", timeout=1)
        json_health = json.loads(o.text)
        assert json_health['status'] == 'UP' or json_health['status']['code'] == 'UP'

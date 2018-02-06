import json
import re
import subprocess
import yaml
import os
from os import listdir

from features.support.app import BusyWait
from features.support.http import url_for
from features.support.repository import LocalConfig

GLOBAL_CONFIG_NAME = 'global-config'
CONFIG_FILE_NAME = 'global.yml'


class K8sDriver:
    def __init__(self, namespace, minikube=None):
        self.namespace = namespace
        self.minikube = minikube

    def wait_to_serve(self, app):
        BusyWait().execute(self.__app_healthy, app)

    def __app_healthy(self, app):
        output = self.__get_in_k8s('%s/health' % url_for(app))
        if json.loads(output)['status']['code'] == 'UP':
            return True
        raise Exception('app %s not healthy' % app.name())

    def __get_in_k8s(self, url):
        return self.__run(
            "kubectl --namespace %s exec deployer-shell -- wget -t 1 -q -O - %s" % (self.namespace, url))

    def verify_app_is_running(self, app):
        BusyWait().execute(self.__pod_running, app.service_name())

    def describe_service(self, service_name):
        return json.loads(self.__run("kubectl --namespace %s get svc %s -o json" % (self.namespace, service_name)))

    def __pod_running(self, image_name):
        pod_name = self.__grab_pod_name(image_name)
        match = re.search(r"Status:\s(.*)", self.__describe_pod(pod_name))
        if match:
            return match.group(1).strip() == 'Running'
        else:
            raise Exception('service %s has no pod!' % pod_name)

    def __describe_pod(self, pod_name):
        return self.__run("kubectl --namespace %s describe pods %s" % (self.namespace, pod_name))

    def describe_deployment(self, app):
        return json.loads(subprocess.check_output(
            "kubectl get --namespace %s deployment %s -o json" % (self.namespace, app), shell=True))

    def __grab_pod_name(self, pod_name):
        output = self.__run("kubectl --namespace %s get pods" % (self.namespace))
        list = output.split()
        for item in list:
            if item.startswith(pod_name):
                return item

    def __run(self, command):
        return subprocess.check_output(command, shell=True)

    def verify_config_is(self, expected_config, conf_entry = "global.yml"):
        assert expected_config == self.__get_k8s_config(conf_entry)

    def verify_all_configs_in_folder(self, folder):
        for file in listdir(folder):
            self.verify_config_is(open(os.path.join(folder, file), 'rb').read(), file)

    def __get_k8s_config(self, config_name = "global.yml"):
        k8s_config_map = self.__run(
            "kubectl get configmap %s --namespace=%s -o yaml" % (GLOBAL_CONFIG_NAME, self.namespace))
        return yaml.load(k8s_config_map)['data'][config_name]

    def delete_namespace(self):
        subprocess.call("kubectl delete namespace %s" % self.namespace, shell=True)

    def create_namespace(self):
        self.__run("kubectl create namespace %s" % self.namespace)

    def create_secret(self, filename, namespace):
        self.__run("kubectl create -f %s --namespace=%s" % (filename, namespace))

    def upload_config(self, path, config="global-config", target_name="global.yml"):
        self.delete_config(config)
        self.__run("kubectl create configmap %s --from-file=%s=%s --namespace=%s" % (
            config, target_name, LocalConfig(path).get_path(), self.namespace))

    def upload_config_folder(self, path, config="global-config"):
        self.delete_config(config)
        self.__run("kubectl create configmap %s --from-file=%s --namespace=%s" % (
            config, LocalConfig(path).get_path(), self.namespace))

    def delete_config(self, config="global-config"):
        subprocess.call(("kubectl delete configmap " + config + " --namespace=%s") % self.namespace, shell=True)

    def scale_deployment(self, deployment, replicas):
        self.__run("kubectl scale --replicas=%s  deployment/%s --namespace=%s" % (
            replicas, deployment, self.namespace))

    @staticmethod
    def add_node_label(name, value):
        subprocess.check_output("kubectl label --overwrite nodes minikube %s=%s" % (name, value), shell=True)

    def verify_get(self, url, verifier):
        return BusyWait(60).execute(self.__verify_output, url, verifier)

    def __verify_output(self, url, verifier):
        output = self.__get_in_k8s(url)
        assert verifier(output), "Failed to verify: %s" % output

    def deploy(self, path):
        subprocess.check_output(
            'kubectl create --namespace %s -f %s' % (self.namespace, path),
            shell=True)


@DeprecationWarning
class ServiceDomainFetcher(object):
    def __init__(self, namespace):
        self._namespace = namespace

    def fetch(self, app, port_name):
        return BusyWait().execute(self.__fetch_helper, app, port_name)

    def __fetch_helper(self, app, port_name):
        svc_json = json.loads(self.__describe_service(app.service_name()))
        return self._extract_domain_from(svc_json, port_name)

    def __describe_service(self, service_name):
        return subprocess.check_output(
            "kubectl get --namespace %s service %s -o json" % (self._namespace, service_name), shell=True)

    def _extract_domain_from(self, svc_json, port_name):
        return 'not implemented'


@DeprecationWarning
class AWSServiceDomainFetcher(ServiceDomainFetcher):
    def __init__(self, namespace):
        super(self.__class__, self).__init__(namespace)

    def _extract_domain_from(self, svc_json, port_name):
        ingress = svc_json['status']['loadBalancer']['ingress']
        if len(ingress) > 0:
            return ['%s:%s' % (ingress[0]['hostname'], p['port'])
                    for p in svc_json['spec']['ports']
                    if p['name'] == port_name][0]
        else:
            raise AttributeError('Failed to find domain in: %s' % svc_json)


class MinikubeServiceDomainFetcher(ServiceDomainFetcher):
    def __init__(self, namespace, minikube_ip):
        super(self.__class__, self).__init__(namespace)
        self.minikube = minikube_ip

    def _extract_domain_from(self, svc_json, port_name):
        return [
            '%s:%s' % (self.minikube, p['nodePort'])
            for p in svc_json['spec']['ports']
            if p['name'] == port_name
        ][0]

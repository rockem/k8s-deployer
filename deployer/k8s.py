import copy
import glob
import os
import re
import subprocess
from time import sleep

from flask import json

from recipe import Recipe
from yml import ByPath
from log import DeployerLogger
from yml import FileYmlCreator
from yml import find_node

logger = DeployerLogger('k8s').getLogger()
CLUSTER_IP_SERVICE = 'ClusterIP'
LOAD_BALANCER_SERVICE = 'LoadBalancer'


class PodHealthChecker(object):
    def __init__(self, connector):
        self.connector = connector

    def health_check(self, pod_name):
        concrete_pod_name = self.__extract_pod_name(pod_name).strip()
        return 'UP' in self.connector.check_pods_health(concrete_pod_name, pod_name)

    def __extract_pod_name(self, pod_name):
        match = re.search(r"Name:\s(.*)", self.connector.describe_pod(pod_name))
        if match:
            return match.group(1)
        else:
            raise Exception('service %s has no pod!' % pod_name)


class ServiceExplorer(object):
    def __init__(self, connector):
        self.connector = connector

    def get_color(self, service_name, default_color='blue'):
        try:
            return json.loads(self.connector.get_service_as_json(service_name))['spec']['selector']['color']
        except subprocess.CalledProcessError as e:
            if e.returncode is not 0:
                return default_color
        except KeyError as e:
            return default_color


class K8sDescriptorFactory(object):
    DEST_DIR = './out/'
    CONTAINERS_LOCATION = 'spec.template.spec.containers'
    DEPLOYMENT_PORTS_LOCATION = 'spec.template.spec.containers'
    service_type_map = {
        Recipe.SERVICE_TYPE_UI: LOAD_BALANCER_SERVICE,
        Recipe.SERVICE_TYPE_API: CLUSTER_IP_SERVICE
    }

    def __init__(self, template_path, configuration):
        self.configuration = configuration
        self.template_path = template_path

    def service(self):
        config = self.__convert_service_type()
        creator = FileYmlCreator(self.template_path, 'service').config(config)
        self.__add_ports(creator, 'service-port', ByPath('spec.ports'))
        return creator.create(self.DEST_DIR)

    def __convert_service_type(self):
        config = copy.deepcopy(self.configuration)
        config['serviceType'] = self.__get_service_type(config)
        return config

    def __get_service_type(self, configuration):
        return self.service_type_map[configuration['serviceType']]

    def __add_ports(self, creator, yml, locator):
        if 'ports' in self.configuration:
            creator.append_many(
                yml,
                locator,
                map(self.__port_props_from, self.configuration['ports']))

    def __port_props_from(self, mapping):
        ports = mapping.split(':')
        return {
            'outPort': ports[0],
            'port': ports[1]
        }

    def deployment(self):
        creator = FileYmlCreator(self.template_path, 'deployment').config(self.configuration)
        self.__add_ports(creator, 'deployment-port', ByContainerPorts(self.configuration['name']))
        return creator.create(self.DEST_DIR)

    def __is_logging_enabled(self):
        return self.configuration.has_key("logging") and self.configuration["logging"] != "none"

    def job(self):
        return FileYmlCreator(self.template_path, 'cronjob').config(self.configuration).create(self.DEST_DIR)


class ByContainerPorts:
    def __init__(self, name):
        self.name = name

    def locate(self, data):
        containers = find_node('spec.template.spec.containers', data)
        for c in containers:
            if c['name'] == self.name:
                return c['ports']
        return None


class K8sConnector(object):
    TEMPLATE_PATH = 'orig'

    def __init__(self, namespace):
        self.namespace = namespace
        self.__create_namespace_if_needed(self.namespace)

    def __create_namespace_if_needed(self, namespace):
        os.popen("kubectl create namespace %s" % namespace)

    def check_pods_health(self, pod_name, container_name):
        # self.__delete_health_file(container_name, pod_name)
        output = self.__exec_on(pod_name, container_name, '-- wget -t 1 -q -O - http://localhost:8080/health')
        # output = self.__exec_on(pod_name, container_name, 'cat health')
        # logger.debug(output)
        return output

    def __delete_health_file(self, container_name, pod_name):
        try:
            self.__exec_on(pod_name, container_name, 'rm health')
            sleep(2)
        except subprocess.CalledProcessError as e:
            print 'Failed to delete health file with error: %s' % e.message

    def __exec_on(self, pod_name, container_name, command):
        return self.__run(
            "kubectl --namespace %s exec %s -c %s %s" % (self.namespace, pod_name, container_name, command))

    def describe_pod(self, pod_name):
        return self.__run("kubectl --namespace %s describe pods %s" % (self.namespace, pod_name))

    def get_service_as_json(self, service_name):
        return self.__run("kubectl --namespace %s get svc %s -o json" % (self.namespace, service_name))

    def cluster_info(self):
        return self.__run("kubectl cluster-info")

    def apply(self, source_to_deploy):
        return self.__run(
            "kubectl --namespace %s apply --validate=false --record -f %s" % (self.namespace, source_to_deploy))

    def apply_service(self, properties):
        self.__run(
            "kubectl --namespace %s apply --validate=false --record -f %s" %
            (self.namespace, K8sDescriptorFactory(self.TEMPLATE_PATH, properties).service()))

    def apply_deployment(self, properties):
        self.__run(
            "kubectl --namespace %s apply --validate=false --record -f %s" %
            (self.namespace, K8sDescriptorFactory(self.TEMPLATE_PATH, properties).deployment()))

    def upload_config_map(self, config_file_path):
        os.system("kubectl --namespace %s delete configmap global-config" % self.namespace)
        return self.__run(
            "kubectl --namespace %s create configmap global-config --from-file=%s" % (self.namespace, config_file_path))

    def upload_job(self, job):
        self.delete_job(job['name'])
        self.__run("kubectl create --namespace %s -f %s" % (
            self.namespace,
            K8sDescriptorFactory(
                self.TEMPLATE_PATH,
                {"job_name": job['name'], "cron": job['schedule'], "url": job['url']}).job()))

    def delete_job(self, job_name):
        os.system("kubectl --namespace %s delete jobs %s" % (self.namespace, job_name))
        os.system("kubectl --namespace %s delete cronjob %s" % (self.namespace, job_name))

    def __run(self, command):
        return subprocess.check_output(command, shell=True)

import glob
import os
import re
import subprocess

from flask import json

from deployer.yml import ByPath
from log import DeployerLogger
from yml import FileYmlCreator
from yml import find_node

logger = DeployerLogger('k8s').getLogger()


class PodHealthChecker(object):
    def __init__(self, connector):
        self.connector = connector

    def health_check(self, pod_name):
        pod_name = self.__extract_pod_name(pod_name).strip()
        logger.debug('pod name after extraction! %s' % pod_name)
        return 'UP' in self.connector.check_pods_health(pod_name)

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


class DeployDescriptorFactory(object):
    DEST_DIR = './out/'
    CONTAINERS_LOCATION = 'spec.template.spec.containers'
    DEPLOYMENT_PORTS_LOCATION = 'spec.template.spec.containers'

    def __init__(self, template_path, configuration):
        self.configuration = configuration
        self.template_path = template_path

    def service(self):
        creator = FileYmlCreator(self.template_path, 'service').config(self.configuration)
        self.__add_ports(creator, 'service-port', ByPath('spec.ports'))
        return creator.create(self.DEST_DIR)

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
        self.__add_logging(creator)
        self.__add_ports(creator, 'deployment-port', ByContainerPorts(self.configuration['name']))
        return creator.create(self.DEST_DIR)

    def __add_logging(self, creator):
        if self.__is_logging_enabled():
            creator.append('fluentd', self.CONTAINERS_LOCATION)

    def __is_logging_enabled(self):
        return self.configuration.has_key("logging") and self.configuration["logging"] != "none"


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

    def check_pods_health(self, pod_name):
        self.__run("kubectl --namespace %s exec -p %s wget http://localhost:8080/health" % (self.namespace, pod_name))
        output = self.__run("kubectl --namespace %s exec -p %s cat health" % (self.namespace, pod_name))
        logger.debug(output)
        try:
            self.__run("kubectl --namespace %s exec -p %s rm health" % (self.namespace, pod_name))
        except subprocess.CalledProcessError as e:
            print e

        return output

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
        return self.__run(
            "kubectl --namespace %s apply --validate=false --record -f %s" %
            (self.namespace, DeployDescriptorFactory(self.TEMPLATE_PATH, properties).service()))

    def apply_deployment(self, properties):
        return self.__run(
            "kubectl --namespace %s apply --validate=false --record -f %s" %
            (self.namespace, DeployDescriptorFactory(self.TEMPLATE_PATH, properties).deployment()))

    def upload_config_map(self, config_file_path):
        os.system("kubectl --namespace %s delete configmap global-config" % self.namespace)
        return self.__run(
            "kubectl --namespace %s create configmap global-config --from-file=%s" % (self.namespace, config_file_path))

    def upload_job(self, job):
        job_config_file = self.__create_job_config_file_from(job)
        self.delete_job(job['name'])
        self.__run("kubectl create --namespace %s -f %s" % (self.namespace, job_config_file))

    def __create_job_config_file_from(self, job):
        return YmlCreator({"job_name": job['name'], "cron": job['schedule'], "url": job['url']},
                          "cronjob_template").create()

    def delete_job(self, job_name):
        os.system("kubectl --namespace %s delete jobs %s" % (self.namespace, job_name))
        os.system("kubectl --namespace %s delete cronjob %s" % (self.namespace, job_name))

    def __run(self, command):
        return subprocess.check_output(command, shell=True)

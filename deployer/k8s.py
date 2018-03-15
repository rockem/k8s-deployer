import copy
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


class AppExplorer(object):
    def __init__(self, connector):
        self.connector = connector

    def get_color(self, service_name, default_color='blue'):
        try:
            return self.connector.describe_service(service_name)['spec']['selector']['color']
        except subprocess.CalledProcessError as e:
            if e.returncode is not 0:
                return default_color
        except KeyError as e:
            return default_color

    def get_deployment_scale(self, service_name, default_scale=1):
        deployment_name = self.get_deployment_name(service_name)
        return default_scale if deployment_name == '' else \
            self.connector.describe_deployment(deployment_name)['spec']['replicas']

    def get_deployment_name(self, service_name):
        try:
            return self.connector.describe_service(service_name)['spec']['selector']['name']
        except (subprocess.CalledProcessError, KeyError, ValueError) as e:
            return ''


class K8sDescriptorFactory(object):
    DEST_DIR = './out/'
    CONTAINERS_LOCATION = 'spec.template.spec.containers'
    DEPLOYMENT_PORTS_LOCATION = 'spec.template.spec.containers'
    service_type_map = {
        Recipe.SERVICE_TYPE_UI: LOAD_BALANCER_SERVICE,
        Recipe.SERVICE_TYPE_API: CLUSTER_IP_SERVICE,
        Recipe.SERVICE_TYPE_INTERNAL_UI: LOAD_BALANCER_SERVICE,
    }

    def __init__(self, template_path, configuration):
        self.configuration = configuration
        self.template_path = template_path

    def service(self):
        config = self.__convert_service_type()
        self.__update_internal_load_balancer(config)
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

    @staticmethod
    def __port_props_from(mapping):
        ports = mapping.split(':')
        return {
            'outPort': ports[0],
            'port': ports[1]
        }

    def __update_internal_load_balancer(self, conf):
        conf['internalLoadBalancerEntry'] = \
            'service.beta.kubernetes.io/aws-load-balancer-internal: 0.0.0.0/0' \
                if self.configuration['serviceType'] == Recipe.SERVICE_TYPE_INTERNAL_UI else ''

    def deployment(self):
        creator = FileYmlCreator(self.template_path, 'deployment').config(self.configuration)
        self.__add_ports(creator, 'deployment-port', ByContainerPorts(self.configuration['name']))
        return creator.create(self.DEST_DIR)

    def service_account(self):
        creator = FileYmlCreator(self.template_path, 'serviceAccount').config(self.configuration)
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
        self.__delete_health_file(container_name, pod_name)
        # output = self.__exec_on(pod_name, container_name, '-- wget -t 1 -q -O - http://localhost:8080/health')
        self.__exec_on(pod_name, container_name, 'wget http://localhost:8080/health')
        output = self.__exec_on(pod_name, container_name, 'cat health')
        logger.debug(output)
        return output

    def __delete_health_file(self, container_name, pod_name):
        try:
            self.__exec_on(pod_name, container_name, 'rm health')
            sleep(1)
        except subprocess.CalledProcessError as e:
            pass

    def __exec_on(self, pod_name, container_name, command):
        return self.__run(
            "kubectl --namespace %s exec %s -c %s %s" % (self.namespace, pod_name, container_name, command))

    def describe_pod(self, pod_name):
        return self.__run("kubectl --namespace %s describe pods %s" % (self.namespace, pod_name))

    def describe_deployment(self, app):
        return json.loads(subprocess.check_output(
            "kubectl get --namespace %s deployment %s -o json" % (self.namespace, app), shell=True))

    def describe_service(self, service_name):
        return json.loads(self.__run("kubectl --namespace %s get svc %s -o json" % (self.namespace, service_name)))

    def describe_service_account(self, service_account_name):
        return json.loads(self.__run("kubectl --namespace %s get sa %s -o json" % (self.namespace, service_account_name)))


    def cluster_info(self):
        return self.__run("kubectl cluster-info")

    def scale_deployment(self, deployment_name, scale):
        self.__run_ignore_error(
            'kubectl --namespace %s scale deployment %s --replicas=%d' % (self.namespace, deployment_name, scale))

    def apply(self, source_to_deploy):
        return self.__run(
            "kubectl --namespace %s apply --validate=false --record -f %s" % (self.namespace, source_to_deploy))

    def apply_service(self, properties):
        self.__delete_service_when_type_changed(properties)

        self.__run(
            "kubectl --namespace %s apply --validate=false --record -f %s" %
            (self.namespace, K8sDescriptorFactory(self.TEMPLATE_PATH, properties).service()))

    def __delete_service_when_type_changed(self, properties):
        service_name = properties['serviceName']
        service_type = properties['serviceType']
        if self.__service_exists(service_name):
            logger.info("Service %s exists, fetch its type and recreate it if its current type: \'%s\' was changed." % (
            service_name, K8sDescriptorFactory.service_type_map[service_type]))
            if self.__fetch_service_type(service_name) != K8sDescriptorFactory.service_type_map[service_type]:
                self.__delete_service(service_name)

    def __fetch_service_type(self, service_name):
        service_type = self.describe_service(service_name)['spec']['type']
        logger.info("service type is: %s " % service_type)
        return service_type

    def __service_exists(self, service_name):
        service_exist = True
        try:
            self.describe_service(service_name)
        except subprocess.CalledProcessError as e:
            service_exist = False

        return service_exist

    def __delete_service(self, service_name):
        self.__run('kubectl --namespace %s delete service %s' % (self.namespace, service_name))

    def apply_deployment(self, properties):
        self.__run(
            "kubectl --namespace %s apply --validate=false --record -f %s" %
            (self.namespace, K8sDescriptorFactory(self.TEMPLATE_PATH, properties).deployment()))


    def apply_service_account(self, properties):
        self.__run(
            "kubectl --namespace %s apply --validate=false --record -f %s" %
            (self.namespace, K8sDescriptorFactory(self.TEMPLATE_PATH, properties).service_account()))


    def upload_config_map(self, config_file_path):
        self.__run_ignore_error("kubectl --namespace %s delete configmap global-config" % self.namespace)
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
        self.__run_ignore_error("kubectl --namespace %s delete jobs %s" % (self.namespace, job_name))
        self.__run_ignore_error("kubectl --namespace %s delete cronjob %s" % (self.namespace, job_name))

    def __run(self, command):
        return subprocess.check_output(command, shell=True)

    def __run_ignore_error(self, command):
        os.system(command)

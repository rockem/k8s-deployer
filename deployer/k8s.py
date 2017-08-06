import os
import re
import subprocess

from flask import json

from log import DeployerLogger

logger = DeployerLogger('PodHealthChecker').getLogger()

class K8sDeployer(object):

    def __init__(self, connector):
        self.connector = connector
        print "init K8sDeployer!"

    def deploy(self,target):
        # source_to_deploy = os.path.join('deployer/produce/' + "%s.yml" % target)
        self.connector.cluster_info()
        logger.debug("going to deploy {}".format(target))
        self.connector.apply(target)


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


class Connector(object):
    def __init__(self, namespace):
        self.namespace = namespace
        self.__create_namespace_if_needed(self.namespace)

    def __create_namespace_if_needed(self, namespace):
        os.popen("kubectl create namespace %s" % namespace)

    def __ignore_blue_green(self, pod_name):
        try:
            cmd = "kubectl --namespace %s exec -p %s ls /opt/app/ignore_blue_green" % (self.namespace, pod_name)
            logger.debug("ignore blue green command is %s" % cmd)
            self.__run(cmd)
        except subprocess.CalledProcessError as e:
            logger.debug("this is the exception - %s" % e)
            logger.debug('we didnt find any ignore file so we will check health')
            return True

        return False

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

    def apply(self, sourceToDeploy):
        return self.__run(
            "kubectl --namespace %s apply --validate=false --record -f %s" % (self.namespace, sourceToDeploy))

    def upload_config_map(self, config_file_path):
        os.system("kubectl --namespace %s delete configmap global-config" % (self.namespace))
        return self.__run(
            "kubectl --namespace %s create configmap global-config --from-file=%s" % (self.namespace, config_file_path))

    def __run(self, command):
        return subprocess.check_output(command, shell=True)

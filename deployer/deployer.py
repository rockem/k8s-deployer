import re
import subprocess
import sys

import click
import time
from flask import json
from kubectlconf.sync import S3ConfSync

from deployRunner import DeployRunner
from gitclient.git_client import GitClient
from k8sConfig import k8sConfig
from log import DeployerLogger
from services import ServiceVersionReader, ServiceVersionWriter
from util import ImageNameParser

DEFAULT_COLOR = 'blue'

logger = DeployerLogger('deployer').getLogger()


class DeployCommand(object):
    def __init__(self, image_name, target, git_repository):
        self.image_name = image_name
        self.target = target
        self.git_repository = git_repository
        self.deploy_run = DeployRunner()
        # self.k8s_conf = k8sConfig()

    def run(self):
        self.__validate_image_contains_tag()
        configuration = self.__create_props()
        print configuration
        self.__update_kubectl()
        self.deploy_run.deploy(k8sConfig().by(configuration))
        self.__validate_pods_status("%s-%s" % (configuration["name"], configuration["podColor"]), configuration)
        ServiceVersionWriter(self.git_repository).write(self.target, configuration.get('name'), self.image_name)
        logger.debug("finished deploying image:%s" % self.image_name)

    def __validate_pods_status(self, service_name, configuration):
        counter = 0
        while counter < 5:
            counter = counter +1
            print 'try number -> %s' %counter
            try:
                pod_name = self.__extract_pods_name(service_name)
                print 'this is pods name %s ' % pod_name
                status = self.__is_healthy(pod_name)
                print 'health status of service %s' % status
                self.__cleanup_pod(pod_name)
                if status:
                    print 'we found a status! %s' % status
                    configuration['serviceColor'] = self.__invert_color(configuration['serviceColor'])
                    print 'going to deploy service with configuration: %s' %configuration
                    self.deploy_run.deploy(k8sConfig().service_by(configuration))
                    print 'deployed, breaking out of the loop'
                    break
                else:
                    time.sleep(1)
            except Exception as e:
                print 'this is the error %s' %e
                time.sleep(1)

    def __update_service_color(self, configuration):
        k8sConfig().service_by(configuration)


    def __extract_pods_name(self, service_name):
        output = subprocess.check_output("kubectl describe pods %s" % service_name, shell=True, stderr=subprocess.STDOUT)
        match = re.search(r"Name:\s(.*)", output)
        if match:
            return match.group(1)
        else:
            raise Exception('service %s has no pod!' % service_name)

    def __is_healthy(self, pod_name):
        subprocess.check_output("kubectl exec -p %s wget http://localhost:5000/health" % pod_name, shell=True, stderr=subprocess.STDOUT)
        output = subprocess.check_output("kubectl exec -p %s cat health" % pod_name, shell=True, stderr=subprocess.STDOUT)
        print 'this is health output %s' % output
        retVal = 'UP' in output
        print 'service status is %s' % retVal
        return retVal

    def __cleanup_pod(self, pod_name):
        try:
            print 'going to clean health file from %s' % pod_name
            subprocess.check_output("kubectl exec -p %s rm health" % pod_name, shell=True, stderr=subprocess.STDOUT)
            print 'cleaned health file from %s' % pod_name
        except subprocess.CalledProcessError as e:
            logger.debug('nothing to delete')

    def __create_props(self):
        name = ImageNameParser(self.image_name).name()
        color = self.__calc_service_color(name)
        return {
            'env': self.target,
            'name': name,
            'image': self.image_name,
            'podColor' : self.__invert_color(color),
            'serviceColor' : color
        }

    def __validate_image_contains_tag(self):
        if ':' not in self.image_name:
            logger.error('image_name should contain the tag')
            sys.exit(1)

    def __update_kubectl(self):
        S3ConfSync(self.target).sync()

    def __invert_color(self, color):
        colors = {
            'blue':'green',
            'green' : 'blue'
        }
        return colors[color]

    def __calc_service_color(self, name):
        try:
            output = subprocess.check_output("kubectl get svc %s -o json" % name, shell=True, stderr=subprocess.STDOUT)
            print 'we found a version of %s, its color is %s' %(name, json.loads(output)['spec']['selector']['color'])
            return json.loads(output)['spec']['selector']['color']
        except subprocess.CalledProcessError as e:
            if e.returncode is not 0:
                print 'this is the first time this service is been deployed! this is the color %s' %DEFAULT_COLOR
                return DEFAULT_COLOR

class PromoteCommand(object):
    git_client = GitClient()

    def __init__(self, from_env, to_env, git_repository):
        self.from_env = from_env
        self.to_env = to_env
        self.git_repository = git_repository

    def run(self):
        services_to_promote = ServiceVersionReader(self.git_repository).read(self.from_env)
        for service in services_to_promote:
            DeployCommand(service, self.to_env, self.git_repository).run()


class ActionRunner:
    def __init__(self, image_name, source, target, git_repository):
        self.image_name = image_name
        self.source = source
        self.target = target
        self.git_repository = git_repository

    def run(self, action):
        if action == 'deploy':
            DeployCommand(self.image_name, self.target, self.git_repository).run()
        elif action == 'promote':
            PromoteCommand(self.source, self.target, self.git_repository).run()


@click.command()
@click.argument('action', type=click.Choice(['deploy', 'promote']))
@click.option('--image_name', default=False)
@click.option('--source', default=False)
@click.option('--target')
@click.option('--git_repository')
def main(action, image_name, source, target, git_repository):
    ActionRunner(image_name, source, target, git_repository).run(action)


if __name__ == "__main__":
    main()

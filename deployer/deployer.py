import os

import click
import yaml

from configuration_generator import ConfigurationGenerator
from k8sDeployer import K8sDeployer


@click.argument('image_name', metavar='<image_name>')
@click.option('--target', default="")
@click.command(options_metavar='<options>')
def main(image_name, target):

    configuration = fetch_service_configuration_from_docker(image_name)
    ConfigurationGenerator(configuration).generate('deployer/produce/deployment.yml').by_template('deployer/orig/deployment.yml')
    ConfigurationGenerator(configuration).generate('deployer/produce/service.yml').by_template('deployer/orig/service.yml')
    K8sDeployer('deployer/produce/deployment.yml', target).deploy_to_k8s()
    K8sDeployer('deployer/produce/service.yml', target).deploy_to_k8s()

def fetch_service_configuration_from_docker(image_name): #registry
    configuration = os.popen("docker run " + image_name + " cat /opt/conf/service.yml").read()
    return yaml.load(configuration)

if __name__ == "__main__":
    main()

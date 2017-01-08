import sys

import click
from kubectlconf.sync import S3ConfSync

from deployRunner import DeployRunner
from gitclient.git_client import GitClient
from k8sConfig import k8sConfig
from log import DeployerLogger
from services import ServiceVersionReader, ServiceVersionWriter

logger = DeployerLogger('deployer').getLogger()


class Deployer(object):
    def __init__(self):
        self.deploy_run = DeployRunner()
        self.k8s_conf = k8sConfig()

    def deploy(self, image_name, target, git_repository):
        self.__validate_image_contains_tag(image_name)
        configuration = self.k8s_conf.fetch_service_configuration_from_docker(image_name)
        self.appendExtraProps(configuration, target)
        self.__update_kubectl(target)
        self.deploy_run.deploy(self.k8s_conf.by(configuration))
        ServiceVersionWriter(git_repository).write(target, configuration.get('name'), image_name)
        logger.debug("finished deploying image:%s" % image_name)

    def appendExtraProps(self, configuration, target):
        configuration['env'] = target

    def __validate_image_contains_tag(self, image_name):
        if ':' not in image_name:
            logger.error('image_name should contain the tag')
            sys.exit(1)

    def __update_kubectl(self, target_env):
        S3ConfSync('config-' + target_env).sync()


class Promoter(object):
    git_client = GitClient()

    def promote(self, from_env, to_env, git_repository):
        services_to_promote = ServiceVersionReader(git_repository).read(from_env)
        for service in services_to_promote:
            Deployer().deploy(service, to_env, git_repository)


class ActionRunner:
    def __init__(self, image_name, source, target, git_repository):
        self.image_name = image_name
        self.source = source
        self.target = target
        self.git_repository = git_repository

    def run(self, action):
        if action == 'deploy':
            Deployer().deploy(self.image_name, self.target, self.git_repository)
        elif action == 'promote':
            Promoter().promote(self.source, self.target, self.git_repository)


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

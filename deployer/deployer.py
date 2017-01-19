import os
import sys

import click
from kubectlconf.sync import S3ConfSync

from deployRunner import DeployRunner
from services import ServiceVersionWriter, ServiceVersionReader, ConfigUploader, GlobalConfigFetcher
from util import ImageNameParser, EnvironmentParser, update_kubectl
from k8sConfig import k8sConfig
from log import DeployerLogger

logger = DeployerLogger('deployer').getLogger()


class DeployCommand(object):
    def __init__(self, image_name, target, git_repository):
        self.image_name = image_name
        self.target = target
        self.git_repository = git_repository
        self.deploy_run = DeployRunner()
        self.k8s_conf = k8sConfig()

    def run(self):
        self.__validate_image_contains_tag()
        configuration = self.__create_props()
        update_kubectl(self.target)
        self.deploy_run.deploy(self.k8s_conf.by(configuration), EnvironmentParser(self.target).namespace())
        ServiceVersionWriter(self.git_repository).write(EnvironmentParser(self.target).env_name(),
                                                        configuration.get('name'), self.image_name)
        logger.debug("finished deploying image:%s" % self.image_name)

    def __create_props(self):
        return {
            'env': self.target,
            'name': ImageNameParser(self.image_name).name(),
            'image': self.image_name
        }

    def __validate_image_contains_tag(self):
        if ':' not in self.image_name:
            logger.error('image_name should contain the tag')
            sys.exit(1)


class PromoteCommand(object):
    def __init__(self, from_env, to_env, git_repository):
        self.from_env = from_env
        self.to_env = to_env
        self.git_repository = git_repository

    def run(self):
        services_to_promote = ServiceVersionReader(self.git_repository).read(self.from_env)
        for service in services_to_promote:
            DeployCommand(service, self.to_env, self.git_repository).run()


class ConfigureCommand(object):
    def __init__(self, target, git_repository):
        self.git_repository = git_repository
        self.target = target

    def run(self):
        env_name = EnvironmentParser(self.target).env_name()
        S3ConfSync(env_name).sync()
        ConfigUploader(self.target).upload(GlobalConfigFetcher(self.git_repository).fetch_for(self.target))


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
        elif action == 'configure':
            ConfigureCommand(self.target, self.git_repository).run()


@click.command()
@click.argument('action', type=click.Choice(['deploy', 'promote', 'configure']))
@click.option('--image_name', default=False)
@click.option('--source', default=False)
@click.option('--target')
@click.option('--git_repository')
def main(action, image_name, source, target, git_repository):
    ActionRunner(image_name, source, target, git_repository).run(action)


if __name__ == "__main__":
    main()

import sys

import click
from kubectlconf.sync import S3ConfSync

from deploy import ImageDeployer
from gitclient.git_client import GitClient
from log import DeployerLogger
from services import ServiceVersionReader, ServiceVersionWriter
from util import EnvironmentParser
from util import ImageNameParser

logger = DeployerLogger('deployer').getLogger()


class DeployCommand(object):

    def __init__(self, image_name, target, git_repository):
        self.image_name = image_name
        self.target = target
        self.git_repository = git_repository
        self.image_deployer = ImageDeployer(self.image_name, self.target)

    def run(self):
        self.__validate_image_contains_tag()
        self.__update_kubectl()
        self.image_deployer.deploy()
        ServiceVersionWriter(self.git_repository).write(EnvironmentParser(self.target).env_name(),  ImageNameParser(self.image_name).name(), self.image_name)
        logger.debug("finished deploying image:%s" % self.image_name)

    def __validate_image_contains_tag(self):
        if ':' not in self.image_name:
            logger.error('image_name should contain the tag')
            sys.exit(1)

    def __update_kubectl(self):
        S3ConfSync(EnvironmentParser(self.target).env_name()).sync()


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

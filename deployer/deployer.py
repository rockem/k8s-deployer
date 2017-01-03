import sys
import click
from deployRunner import DeployRunner
from services import ServiceVersionReader, ServiceVersionWriter
from gitclient.GitClient import GitClient
from log import DeployerLogger
from k8sConfig import k8sConfig
from kubectlconf.sync import S3ConfSync

logger = DeployerLogger('deployer').getLogger()


def update_kubectl(to_env):
    S3ConfSync(to_env).sync()


class Deployer(object):

    def __init__(self):
        self.deploy_run = DeployRunner()
        self.k8s_conf = k8sConfig()

    def deploy(self, image_name, target, git_repository):
        self.__validate(image_name)
        configuration = self.k8s_conf.fetch_service_configuration_from_docker(image_name)
        ymls = self.k8s_conf.by(configuration)
        # update_kubectl(to)
        self.deploy_run.deploy(ymls)
        ServiceVersionWriter(git_repository).write(target, configuration.get('name'), image_name)
        logger.debug("finished deploying image:%s" % image_name)

    def __validate(self, image_name):
        if ':' not in image_name:
            logger.error('image_name should contain the tag')
            sys.exit(0)


class Promoter(object):
    git_client = GitClient()

    def promote(self, from_env, to_env, git_repository):
        services_to_promote = ServiceVersionReader(git_repository).read(from_env)
        # update_kubectl(to_env)
        for service in services_to_promote:
            Deployer().deploy(service, to_env, git_repository)


@click.command()
@click.option('--action')
@click.option('--image_name', default=False)
@click.option('--source', default=False)
@click.option('--target')
@click.option('--git_repository')
def main(action, image_name, source, target, git_repository):
    if action == 'deploy':
        Deployer().deploy(image_name, target, git_repository)
    elif action == 'promote':
        Promoter().promote(source, target, git_repository)
    else:
        logger.error('deploy/promote are the only allowed actions')
        sys.exit(0)

if __name__ == "__main__":
    main()

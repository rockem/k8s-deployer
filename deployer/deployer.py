import sys
import click
from deployRunner import DeployRunner
from services import ServiceVersionReader, ServiceVersionWriter
from gitclient.GitClient import GitClient
from log import DeployerLogger
from k8sConfig import k8sConfig
import subprocess

logger = DeployerLogger('deployer').getLogger()


def update_kubectl(to_env):
    subprocess.check_output('kubectl-conf' + ' config-' + to_env, shell=True)


class Deployer(object):

    def deploy(self, image_name, target, git_repository):
        self.__validate(image_name)
        k8s_conf = k8sConfig()
        deploy_run = DeployRunner()
        configuration = k8s_conf.fetch_service_configuration_from_docker(image_name)
        ymls = k8s_conf.by(configuration)
        # update_kubectl(to)
        deploy_run.deploy(ymls)
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

    # def __get_services_to_promote(self, from_env):
    #     self.git_client.delete_checkout_dir(DeployRunner.CHECKOUT_DIRECTORY)
    #     self.git_client.get_repo(DeployRunner.SERVICES_ENVS_REPO,
    #                              DeployRunner.CHECKOUT_DIRECTORY)
    #
    #     return self.__get_images_to_deploy(DeployRunner.CHECKOUT_DIRECTORY + '/' + from_env +
    #                                        DeployRunner.SERVICES_FOLDER)
    #
    # def __get_images_to_deploy(self, services_path):
    #     images_to_deploy = []
    #     for filename in os.listdir(services_path):
    #         file_path = os.path.join(services_path, filename)
    #         srv_yml_file = open(file_path, 'r')
    #         image_dict = yaml.load(srv_yml_file)
    #         image_name = image_dict.get(DeployRunner.IMAGE_NAME)
    #         images_to_deploy.append(image_name)
    #     return images_to_deploy


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

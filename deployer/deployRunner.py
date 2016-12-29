from gitclient.GitClient import GitClient
from k8sDeployer import K8sDeployer
from deployerLogger import DeployerLogger

logger = DeployerLogger(__name__).getLogger()

class DeployRunner(object):
    CHECKOUT_DIRECTORY = 'tmp'
    SERVICES_ENVS_REPO = 'https://git.dnsk.io/media-platform/k8s-services-envs'
    git_client = GitClient()

    def deploy(self, ymls=[]):
        for yml in ymls:
            K8sDeployer().deploy(yml).to()

    def update_service_version(self, configuration, to):
        service_name = configuration.get('name')
        service_version = configuration.get('version')
        self.git_client.delete_checkout_dir(self.CHECKOUT_DIRECTORY)
        repo = self.git_client.get_repo(self.SERVICES_ENVS_REPO, self.CHECKOUT_DIRECTORY)
        srv_directory = to + '/services/'
        self.git_client.init_directory(self.CHECKOUT_DIRECTORY + '/' + srv_directory)
        file_name = srv_directory + service_name + '.yml'
        self.__write_service_file(self.CHECKOUT_DIRECTORY, file_name, service_version)
        self.git_client.push(file_name, repo, service_name, service_version)
        logger.info('finished updating %s repository(if necessary) with %s service name and %s service version'
                    % (self.SERVICES_ENVS_REPO, service_name, service_version))

    def __write_service_file(self, checkout_directory, file_name, service_version):
        service_file = open(checkout_directory + '/' + file_name, 'w')
        service_file.write('version: %s' % service_version)
        service_file.close()

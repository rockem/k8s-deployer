import click
from commands import WriteToLogCommandRegularDeploy, DeployCommand, PromoteCommand, ConfigureCommand, \
    RollbackCommand
from deploy import DeployError
from k8s import K8sConnector
from log import DeployerLogger
from recipe import Recipe
from repository import MongoDeploymentRepository, DummyMongoConnector
from util import EnvironmentParser
from yml import YmlReader

logger = DeployerLogger('deployer').getLogger()


class ActionRunner:
    def __init__(self, image_name, source, target, git_repository, domain, recipe_path, timeout, yml_path,
                 service_name, mongo_uri):
        self.image_name = image_name
        self.source = source
        self.target = target
        self.git_repository = git_repository
        self.domain = domain
        self.recipe_path = recipe_path
        self.timeout = timeout
        self.yml_path = yml_path
        self.service_name = service_name
        self.mongo_uri = mongo_uri

    def run(self, action):
        mongo_connector = self.__get_mongo_connector(self.mongo_uri)
        connector = K8sConnector(EnvironmentParser(self.target).namespace())
        if action == 'deploy':
            recipe = Recipe.builder().ingredients(YmlReader(self.recipe_path).read()).image(self.image_name).build()
            env = EnvironmentParser(self.target).name()
            WriteToLogCommandRegularDeploy(mongo_connector, recipe, env,
                                           DeployCommand(self.target, self.git_repository, self.domain, connector,
                                                         recipe, self.timeout)).run()
        elif action == 'promote':
            PromoteCommand(self.source, self.target, self.git_repository, self.domain, connector, self.timeout,
                           mongo_connector).run()
        elif action == 'configure':
            ConfigureCommand(self.target, self.git_repository, connector).run()
        elif action == 'rollback':
            RollbackCommand(self.target, self.git_repository, self.domain, connector, self.timeout,
                            self.service_name, mongo_connector).run()
        else:
            raise DeployError('Unknown command %s' % action)

    def __get_mongo_connector(self, mongo_uri):
        return DummyMongoConnector() if mongo_uri == '' else MongoDeploymentRepository(self.mongo_uri)


@click.command()
@click.argument('action', type=click.Choice(['deploy', 'promote', 'configure', 'rollback']))
@click.option('--image_name', default=False)
@click.option('--source', default=False)
@click.option('--target')
@click.option('--git_repository')
@click.option('--domain', default="")
@click.option('--recipe', default="")
@click.option('--deploy-timeout', default=120)
@click.option('--yml_path', default="")
@click.option('--service_name', default="")
@click.option('--mongo_uri', default="")
def main(action, image_name, source, target, git_repository, domain, recipe, deploy_timeout, yml_path, service_name,
         mongo_uri):
    ActionRunner(image_name, source, target, git_repository, domain, recipe, deploy_timeout, yml_path,
                 service_name, mongo_uri).run(
        action)


if __name__ == "__main__":
    main()

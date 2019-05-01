import click

from commands import PromoteCommand, ConfigureCommand, \
    RollbackCommand, DeploymentCommand
from deploy import DeployError
from log import DeployerLogger

logger = DeployerLogger('deployer').getLogger()

ACTIONS = {
    "deploy": DeploymentCommand,
    "promote": PromoteCommand,
    "configure": ConfigureCommand,
    "rollback": RollbackCommand
}


class ActionRunner:

    def __init__(self, action, args):
        self.action = action
        self.args = args

    def run(self):
        action_callback = ACTIONS.get(self.action)
        if action_callback:
            action_callback(self.args).run()
        else:
            raise DeployError('Unknown command %s' % self.action)


@click.command()
@click.argument('action', type=click.Choice(ACTIONS.keys()))
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
@click.option('--autoscale-min-pods', default=1)
@click.option('--autoscale-max-pods', default=10)
@click.option('--force', is_flag=True, required=False)
def main(action, **args):
    print("this is args %s" % args)
    ActionRunner(action, args).run()


if __name__ == "__main__":
    main()

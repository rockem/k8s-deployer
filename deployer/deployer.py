import click

from deployRunner import deployRunner
from deployerLogger import DeployerLogger
from k8sConfig import k8sConfig
logger = DeployerLogger('deployer').getLogger()

@click.argument('image_name', metavar='<image_name>')
@click.command(options_metavar='<options>')
def main(image_name):

    deployRunner().deploy(k8sConfig().by(image_name))
    logger.debug("%s deployed successfully" %(image_name))

if __name__ == "__main__":
    main()

import click

from deployRunner import DeployRunner
from deployerLogger import DeployerLogger
from k8sConfig import k8sConfig
logger = DeployerLogger('deployer').getLogger()


@click.argument('to', metavar='<to>')
@click.argument('image_name', metavar='<image_name>')
@click.command(options_metavar='<options>')
def main(image_name, to):
    k8s_conf = k8sConfig()
    deploy_run = DeployRunner()
    configuration = k8s_conf.fetch_service_configuration_from_docker(image_name)
    ymls = k8s_conf.by(configuration)
    deploy_run.deploy(ymls)
    deploy_run.update_service_version(configuration, to)
    logger.debug("finished deploying image:%s" % image_name)

if __name__ == "__main__":
    main()

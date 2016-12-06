import click

from deployRunner import deployRunner
from k8sConfig import k8sConfig


@click.argument('image_name', metavar='<image_name>')
@click.command(options_metavar='<options>')
def main(image_name):

    deployRunner().deploy(k8sConfig().by(image_name))

if __name__ == "__main__":
    main()

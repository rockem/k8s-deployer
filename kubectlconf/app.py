import click


from sync import S3ConfSync


@click.command()
@click.argument('environment_name', metavar='<environment_name>', nargs=1)
def main(environment_name):
    """Configures the machine to be able to connect to an existing remote k8s setup with kubectl.
       Copies the relevant files from a specific s3 folder.
       Look at s3 under agt-terraform-state-prod to verify the environment name."""
    S3ConfSync(environment_name).sync()


if __name__ == "__main__":
    main()


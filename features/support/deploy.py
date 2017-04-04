import os

import subprocess


class DeployerDriver:
    def __init__(self, git_repo, target):
        self.git_repo = git_repo
        self.target = target

    def deploy(self, name, should_fail=False):
        try:
            self.run_deploy_command(name)
        except subprocess.CalledProcessError as e:
            if not should_fail:
                raise e

    def run_deploy_command(self, name):
        recipe_option = '--recipe %s' % self.__get_recipe_path(name)
        subprocess.check_output(
            "python deployer/deployer.py deploy --image_name %s --target %s "
            "--git_repository %s --deploy-timeout=5 %s" % (name, self.target, self.git_repo, recipe_option),
            shell=True,
            stderr=subprocess.STDOUT)

    def __get_recipe_path(self, name):
        path = "./features/apps/%s/recipe.yml" % name
        if os.path.isfile(path):
            return os.path.realpath(path)
        return ''

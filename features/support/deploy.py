import os

import subprocess

from features.support.docker import AppImage


class DeployDriverError(Exception):
    pass


class DeployerDriver:
    def __init__(self, git_repo, target):
        self.git_repo = git_repo
        self.target = target

    def deploy(self, app_image, should_fail=False):
        try:
            self.run_deploy_command(app_image)
            if should_fail:
                raise DeployDriverError()
        except subprocess.CalledProcessError as e:
            if not should_fail:
                print(e.output)
                raise e

    def __run(self, command):
        try:
            print("os.environ.get %s" % os.environ.get('TARGET_ENV'))
            subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print("command %s fail - %s" % (command, e.output))
            raise e

    def run_deploy_command(self, app_image):
        self.__run(
            "python deployer/deployer.py deploy --image_name %s --target %s --git_repository %s --deploy-timeout=20 %s" % (
                app_image.image_name(), self.target, self.git_repo,
                self.__get_recipe_option_for(app_image.recipe_path())))

    def __get_recipe_option_for(self, path):
        if os.path.isfile(path):
            recipe = os.path.realpath(path)
        else:
            recipe = "\"logging: none\""
        return '--recipe %s' % recipe

    def configure(self):
        self.__run(
            "python deployer/deployer.py configure --target %s --git_repository %s" % (self.target, self.git_repo))

    def promote(self):
        self.__run("python deployer/deployer.py promote --source int --target %s --git_repository %s" % (
            self.target, self.git_repo))

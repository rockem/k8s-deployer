import os

import subprocess

from features.support.docker import AppImage

APP = "deployer/app.py"


class DeployDriverError(Exception):
    pass


class DeployerDriver:
    def __init__(self, git_repo, target, domain, swagger_path=''):
        self.git_repo = git_repo
        self.target = target
        self.domain = domain
        self.swagger_path = swagger_path

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
            subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print("command %s fail - %s" % (command, e.output))
            raise e

    def run_deploy_command(self, app_image):
        self.__run(
            "python %s deploy --image_name %s --target %s --git_repository %s --domain=%s --deploy-timeout=20 %s" % (
                APP, app_image.image_name(), self.target, self.git_repo, self.domain,
                self.__get_recipe_option_for(app_image.recipe_path())))

    def __get_recipe_option_for(self, path):
        if os.path.isfile(path):
            recipe = os.path.realpath(path)
        else:
            recipe = "\"logging: none\""
        return '--recipe %s' % recipe

    def configure(self):
        self.__run(
            "python %s configure --target %s --git_repository %s" % (APP, self.target, self.git_repo))

    def promote(self):
        self.__run("python %s promote --source int --target %s --git_repository %s" % (
            APP, self.target, self.git_repo))

    def deploy_swagger(self, path):
        self.__run(
            "python %s swagger  --target %s  --swagger_yml_path %s " % (APP,self.target,path))

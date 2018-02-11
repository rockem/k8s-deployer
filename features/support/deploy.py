import os

import subprocess


APP = " python deployer/app.py"


class DeployDriverError(Exception):
    pass


class DeployerDriver:
    def __init__(self, git_repo, target, domain):
        self.git_repo = git_repo
        self.target = target
        self.domain = domain


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
            "%s deploy --image_name %s --target %s --git_repository %s --domain=%s --deploy-timeout=20 %s" % (
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
            "%s configure --target %s --git_repository %s" % (APP, self.target, self.git_repo))

    def promote(self, source_env):
        self.__run("%s promote --source %s --target %s --git_repository %s" % (
            APP,source_env, self.target, self.git_repo))

    def deploy_swagger(self, path):
        self.__run("%s swagger --git_repository %s --yml_path %s" % (APP, self.git_repo, path))

    def rollback(self, service_name):
            self.__run(
                "%s rollback --target %s --git_repository %s --domain=%s --deploy-timeout=20 --service_name=%s" % (
                    APP, self.target, self.git_repo, self.domain, service_name))
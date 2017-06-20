import os

import subprocess


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


    def run_deploy_command(self, app_image):
        subprocess.check_output(
            "python deployer/deployer.py deploy --image_name %s --target %s "
            "--git_repository %s --deploy-timeout=20 %s" %
            (app_image.image_name(), self.target, self.git_repo, self.__get_recipe_option_for(app_image.recipe_path())),
            shell=True,
            stderr=subprocess.STDOUT)

    def __get_recipe_option_for(self, path):
        recipe_option = ''
        if os.path.isfile(path):
            recipe_option = '--recipe %s' % os.path.realpath(path)
        return recipe_option

    def configure(self):
        subprocess.check_output(
            "python deployer/deployer.py configure --target %s --git_repository %s" %
            (self.target, self.git_repo),
            shell=True, stderr=subprocess.STDOUT)

    def promote(self):
        try:
            subprocess.check_output("python deployer/deployer.py promote --source int --target %s "
                                    "--git_repository %s" % (self.target, self.git_repo),
                                    shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(e.output)
            raise e


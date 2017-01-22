import os
import shutil

import yaml

from behave import *
from deployer.gitclient.git_client import GitClient
from features.steps.support import GIT_REPO_URL, TARGET_ENV, TARGET_ENV_AND_NAMESPACE, NAMESPACE

use_step_matcher("re")
CHECKOUT_DIRECTORY = 'tmp'
SERVICES_FOLDER = '/services/'
IMAGE_NAME = 'image_name'
git_client = GitClient(GIT_REPO_URL)
CONFIG_FILE_NAME = 'global.yml'
K8S_NAME = 'global-config'


@given("config file exists in git")
def push_to_git(context):
    ConfigFilePusher(GIT_REPO_URL).write(TARGET_ENV, get_local_config_file_path())


def get_local_config_file_path():
    abs_file_path = os.getcwd() + "/features/config/global.yml"
    return abs_file_path


@when("configuring")
def executing(context):
    assert os.system("python deployer/deployer.py configure --target %s --git_repository %s" %
                     (TARGET_ENV_AND_NAMESPACE, GIT_REPO_URL)) == 0

@then("config uploaded to k8s")
def deploy(context):
    k8s_configmap_data = get_configmap_k8s()
    local_config_map = get_local_configmap_data()
    assert k8s_configmap_data == local_config_map


def get_local_configmap_data():
    return open(get_local_config_file_path(), 'rb').read()


def get_configmap_k8s():
    configmap_content = os.popen("kubectl get configmap %s --namespace=%s -o yaml" % (K8S_NAME, NAMESPACE)).read()
    configmap_data = yaml.load(configmap_content)['data'][CONFIG_FILE_NAME]
    return configmap_data


class ConfigFilePusher:
    CHECKOUT_DIRECTORY = 'tmp'

    def __init__(self, git_repository):
        self.git_url = git_repository

    def write(self, env, config_file):

        # shutil.rmtree(CHECKOUT_DIRECTORY)
        if os.path.exists( CHECKOUT_DIRECTORY ):
            shutil.rmtree( CHECKOUT_DIRECTORY )
        os.system("git clone %s %s" % (self.git_url, CHECKOUT_DIRECTORY))
        self.__copy_config(config_file, "%s/%s" % (self.CHECKOUT_DIRECTORY, env))
        curr_dir = os.getcwd()
        os.chdir(CHECKOUT_DIRECTORY)
        os.system("git add . && git commit -m 'Updated configuration'")
        os.system("git push")
        os.chdir(curr_dir)


    def __copy_config(self, file_name, config_dir):
        os.makedirs(config_dir)
        shutil.copy(file_name, config_dir)

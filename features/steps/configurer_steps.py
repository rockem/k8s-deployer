import os
import shutil

import yaml

from behave import *
from deployer.gitclient.git_client import GitClient
from features.steps.support import GIT_REPO_URL, TARGET_ENV, TARGET_ENV_AND_NAMESPACE, NAMESPACE, delete_namespace

use_step_matcher("re")
SERVICES_FOLDER = '/services/'
IMAGE_NAME = 'image_name'
git_client = GitClient(GIT_REPO_URL)
CONFIG_FILE_NAME = 'global.yml'
K8S_NAME = 'global-config'

@given('namespace "(.+)" doesn\'t exists')
def clear_namespace(context, namespace=None):
    delete_namespace(namespace)

@when("configuring(?: \"(.+)\")?")
def executing(context, namespace = None):
    target = TARGET_ENV_AND_NAMESPACE if namespace is None else "%s:%s" % (TARGET_ENV, namespace)
    assert os.system("python deployer/deployer.py configure --target %s --git_repository %s" %
                     (target, GIT_REPO_URL)) == 0


@then("config uploaded(?: to \"(.+)\" namespace)?")
def validate_config_uploaded(context, namespace=None):
    k8s_configmap_data = get_configmap_k8s(namespace)
    local_config_map = get_local_configmap_data()
    assert k8s_configmap_data == local_config_map
    delete_namespace(namespace)


def get_local_configmap_data():
    return open(get_local_config_file_path(), 'rb').read()

def get_local_config_file_path():
    abs_file_path = os.getcwd() + "/features/config/global.yml"
    return abs_file_path

def get_configmap_k8s(namespace):
    namespace = NAMESPACE if namespace is None else namespace
    configmap_content = os.popen("kubectl get configmap %s --namespace=%s -o yaml" % (K8S_NAME, namespace)).read()
    configmap_data = yaml.load(configmap_content)['data'][CONFIG_FILE_NAME]
    return configmap_data


class ConfigFilePusher:
    CHECKOUT_DIRECTORY = 'feature_tmp'

    def __init__(self, git_repository):
        self.git_url = git_repository

    def write(self, env, config_file):

        if os.path.exists( self.CHECKOUT_DIRECTORY ):
            shutil.rmtree( self.CHECKOUT_DIRECTORY )
        os.system("git clone %s %s" % (self.git_url, self.CHECKOUT_DIRECTORY))
        self.__copy_config(config_file, "%s/%s" % (self.CHECKOUT_DIRECTORY, env))
        old_dir = os.getcwd()
        os.chdir(self.CHECKOUT_DIRECTORY)
        os.system("git add . && git commit -m 'Updated configuration' && git push")
        os.chdir(old_dir)

    def __copy_config(self, file_name, config_dir):
        os.makedirs(config_dir)
        shutil.copy(file_name, config_dir)

import os
import shutil

from deployer.gitclient.GitClient import GitClient

REPO_NAME = 'behave_repo'


def before_scenario(context, scenario):
    print 'in before_scenario'
    delete_repo()
    GitClient().init(REPO_NAME)


def delete_repo():
    print 'in delete_repo'
    if os.path.exists(REPO_NAME):
        shutil.rmtree(REPO_NAME)


def after_scenario(context, scenario):
    print 'in after_scenario'
    # delete_repo()

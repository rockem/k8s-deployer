import os
import shutil

import git

CHECKOUT_DIR = 'tmp'

class GitClient(object):
    repo = None

    def __init__(self, git_url):
        self.git_url = git_url

    def checkout(self):
        if os.path.exists(CHECKOUT_DIR):
            shutil.rmtree(CHECKOUT_DIR)
        self.repo = git.Repo.clone_from(self.git_url, CHECKOUT_DIR)

    def check_in(self):
        self.repo.git.add('--all')
        self.repo.index.commit("Update by deployer")
        self.repo.remote().push()

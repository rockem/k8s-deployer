import shutil

import git
import os


class GitClient(object):
    CHECKOUT_DIR = 'tmp'

    _repo = None

    def __init__(self, git_url):
        self._git_url = git_url

    def checkout(self):
        if os.path.exists(self.CHECKOUT_DIR):
            shutil.rmtree(self.CHECKOUT_DIR)
        self._repo = git.Repo.clone_from(self._git_url, self.CHECKOUT_DIR)

    def check_in(self):
        self._repo.git.add('--all')
        if self._repo.is_dirty():
            self._repo.index.commit("Update by deployer")
            self._repo.remote().push()

    def retrieve_previous_commit_file(self, file_name):
        commit = self.get_previous_commit(file_name)
        blob = commit.tree[file_name]
        return blob.data_stream.read()

    def get_previous_commit(self, file_name, max_count=2):
        try:
            commits = self._repo.iter_commits(max_count=max_count, paths=file_name)
            commit = commits.next()
            commit = commits.next()
        except StopIteration as e:
            raise NotEnoughCommitsError(e)
        return commit


class NotEnoughCommitsError(Exception):
    def __init(self, message):
        super(NotEnoughCommitsError, self).__init__(message)
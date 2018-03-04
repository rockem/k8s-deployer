import os

import git

from deployer.git_util import GitClient


class TestGitUtil(object):

    def setup(self):
        git.Repo.init('it_repo', bare=True)
        self.git_client = GitClient("it_repo")
        self.git_client.checkout()

    def test_should_not_push_if_no_changes(self):
        self._commit_something()
        commit_id = self._get_current_commit_id()
        self._push_and_clone()
        assert self._get_current_commit_id() == commit_id

    def _commit_something(self):
        path = os.path.join(self.git_client.CHECKOUT_DIR, 'file.txt')
        with open(path, 'w') as outfile:
            outfile.write('something')
        self.git_client.check_in()

    def _get_current_commit_id(self):
        return git.Repo(GitClient.CHECKOUT_DIR).commit()

    def _push_and_clone(self):
        self.git_client.check_in()
        self.git_client.checkout()
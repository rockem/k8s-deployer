from nose.tools import raises, with_setup
from deployer.repository import DeployLogRepository
import git
import os
import shutil
import yaml
import errno
from deployer.git_util import NotEnoughCommitsError


class GitRepositoryClient(object):
    CHECKOUT_DIR = 'tmp'
    
    def __init__(self, repo_name):
        self._repo_name = repo_name
        self.git_url = self.__git_url_for(repo_name)

    def create(self):
        if os.path.exists(self._repo_name):
            shutil.rmtree(self._repo_name)
        return git.Repo.init(self._repo_name, bare=True)

    def clone_repo(self):
        if os.path.exists(self.CHECKOUT_DIR):
            shutil.rmtree(self.CHECKOUT_DIR)
        self.repo = git.Repo.clone_from(self.__git_url_for(self._repo_name), self.CHECKOUT_DIR)

    def __git_url_for(self, repo_name):
        return "file://" + os.getcwd() + '/' + repo_name

    def retrieve_git_url(self):
        return self.__git_url_for(self._repo_name)

    def commit_and_push(self, message):
        self.repo.git.add('--all')
        self.repo.index.commit(message)
        self.repo.remote().push()


class TestDeployLogRepository(object):
    TEST_YML_FILE_NAME = "data"
    NUM_OF_COMMITS = 3
    TXT1 = "HelloWorld"
    TXT2 = "GitPython"
    TXT3 = {'url' : 'blabla'}
    TARGET = "MyTarget"

    def setup(self):
        self.git_client = GitRepositoryClient("rollback_repo")
        self.git_repo = self.git_client.create()
        self.git_client.clone_repo()
        self.repository = DeployLogRepository(self.git_client.git_url, self.TARGET)


    def test_retrieve_previous_version(self):
        self.push_yaml(self.TXT1, 'services', self.TEST_YML_FILE_NAME)
        self.push_yaml(self.TXT2, 'services', self.TEST_YML_FILE_NAME)
        previous_yml = self.repository.get_previous_recipe(self.TEST_YML_FILE_NAME)
        assert previous_yml == self.TXT1

    def test_retrieve_swagger(self):
        self.push_yaml(self.TXT3, 'api', 'swagger')
        assert self.repository.get_swagger()['url'] == 'blabla'

    def push_yaml(self, data, env, file_name):
        yml_test_file_path = os.path.join(
            GitRepositoryClient.CHECKOUT_DIR, self.TARGET, env, file_name + ".yml")
        self.__create_yml_file(data, yml_test_file_path)
        self.git_client.commit_and_push("adding yml test file with data: %s" % data)
        return data

    @raises(NotEnoughCommitsError)
    def test_should_fail_when_not_enough_commits(self):
        self.push_yaml(self.TXT1, 'services', self.TEST_YML_FILE_NAME)
        self.repository.get_previous_recipe(self.TEST_YML_FILE_NAME)

    @staticmethod
    def __create_yml_file(data, output_path="data.yml"):
        if not os.path.exists(os.path.dirname(output_path)):
            try:
                os.makedirs(os.path.dirname(output_path))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(output_path, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)







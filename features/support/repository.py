import errno
import os
import shutil
from os import listdir
import git
import yaml


class GitRepository(object):
    def __init__(self, repo_name, checkout_dir):
        self._repo_name = repo_name
        self._checkout_dir = checkout_dir

    def create(self):
        if os.path.exists(self._repo_name):
            shutil.rmtree(self._repo_name)
        repo = git.Repo()
        repo.init(self._repo_name, bare=True)

    def _checkout_repo(self):
        if os.path.exists(self._checkout_dir):
            shutil.rmtree(self._checkout_dir)
        return git.Repo.clone_from(self.__git_url_for(self._repo_name), self._checkout_dir)

    def __git_url_for(self, repo_name):
        return "file://" + os.getcwd() + '/' + repo_name


class LoggingRepository(GitRepository):
    REPO_NAME = 'env_repo'
    GIT_REPO_URL = "file://" + os.getcwd() + '/' + REPO_NAME
    CHECKOUT_DIR = 'env_co'

    def __init__(self):
        super(LoggingRepository, self).__init__(self.REPO_NAME, self.CHECKOUT_DIR)

    def verify_app_is_logged(self, app):
        super(LoggingRepository, self)._checkout_repo()
        assert self.get_recipe_for(app)['image_name'] == app.image_name()

    def get_recipe_for(self, app):
        return yaml.load(open(os.path.join(self.CHECKOUT_DIR, 'int', 'services', '%s.yml' % app.service_name()), "r"))

    @staticmethod
    def recipe_content(app):
        return {'image_name': app.image_name(), 'logging': 'none'}

    @staticmethod
    def recipe_location(env):
        return os.path.join(LoggingRepository.CHECKOUT_DIR, env, "services/recipe.yml")

    @staticmethod
    def swagger_location(env):
        return os.path.join(LoggingRepository.CHECKOUT_DIR, env, "api/swagger.yml")

    def log(self, path, data):
        repo = super(LoggingRepository, self)._checkout_repo()
        FileCreator.create_for(path, data)
        repo.git.add('--all')
        repo.index.commit("updated by tests")
        repo.remote().push()

class FileCreator():
    @staticmethod
    def create_for(path, data):
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

        with open(path, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

    @staticmethod
    def delete_from(path):
        try:
            os.remove(path)
        except OSError:
            print 'recipe path not found'




class ConfigRepository(GitRepository):
    REPO_NAME = 'config_repo'
    GIT_REPO_URL = "file://" + os.getcwd() + '/' + REPO_NAME
    CHECKOUT_DIR = 'config_co'
    GLOBAL_CONFIG_PATH = CHECKOUT_DIR + '/int/global-configs/global.yml'
    MAIN_CONFIG_PATH = CHECKOUT_DIR + '/int/global-configs/'

    JOBS_PATH = CHECKOUT_DIR + '/int/jobs.yml'

    def __init__(self):
        super(ConfigRepository, self).__init__(self.REPO_NAME, self.CHECKOUT_DIR)

    def push_job(self, job_config):
        config_dict = {job_config: self.JOBS_PATH,
                       "default.yml": self.GLOBAL_CONFIG_PATH}
        self.__push(config_dict)

    def push_config(self, config_name):
        config_dict = {config_name: self.GLOBAL_CONFIG_PATH}
        self.__push(config_dict)

    def push_config_folder(self, config_name):
        config_dict = {config_name: self.MAIN_CONFIG_PATH}
        self.__push(config_dict)

    def __push(self, config_dict):
        repo = super(ConfigRepository, self)._checkout_repo()
        for source, target in config_dict.iteritems():
            self._copy_file_or_dir(source, target)
        repo.git.add('--all')
        repo.index.commit("updated by tests")
        repo.remote().push()

    def _copy_file_or_dir(self, source, target):
        if os.path.isdir(LocalConfig(source).get_path()):
            self._copytree(LocalConfig(source).get_path(), target)
        else:
            self._copy(source, target)

    @staticmethod
    def _copy(source, target):
        ConfigRepository._create_dir_if_not_exist(target)
        shutil.copyfile(LocalConfig(source).get_path(), target)

    @staticmethod
    def _copytree(src, dst, symlinks=False, ignore=None):
        ConfigRepository._create_dir_if_not_exist(dst)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            shutil.copyfile(s, dst + item)

    @staticmethod
    def _create_dir_if_not_exist(dst):
        if not os.path.exists(os.path.dirname(dst)):
            try:
                os.makedirs(os.path.dirname(dst))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise


class LocalConfig:
    def __init__(self, name):
        self.name = name

    def content(self):
        return open(self.__get_config_path(), 'rb').read()

    def __get_config_path(self):
        return 'features/config/%s' % self.name

    def get_path(self):
        return self.__get_config_path()

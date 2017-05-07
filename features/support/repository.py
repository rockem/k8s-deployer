import os
import shutil

import errno
import git
import yaml

REPO_NAME = 'behave_repo'
GIT_REPO_URL = "file://" + os.getcwd() + '/' + REPO_NAME
CHECKOUT_DIR = 'behave_co'


class RecipeRepository:
    def __init__(self):
        pass

    def create(self):
        if os.path.exists(REPO_NAME):
            shutil.rmtree(REPO_NAME)
        repo = git.Repo()
        repo.init(REPO_NAME, bare=True)

    def verify_app_is_logged(self, app):
        self.__checkout_repo()
        assert self.get_recipe_for(app)['image_name'] == app.image_name()

    def get_recipe_for(self, app):
        return yaml.load(open(os.path.join(CHECKOUT_DIR, 'int', 'services', '%s.yml' % app.service_name()), "r"))

    def __checkout_repo(self):
        if os.path.exists(CHECKOUT_DIR):
            shutil.rmtree(CHECKOUT_DIR)
        git.Repo.clone_from(GIT_REPO_URL, CHECKOUT_DIR)

    def verify_recipe_is_logged_for(self, app):
        self.__checkout_repo()
        source_recipe = yaml.load(open(app.recipe_path(), "r"))
        recipe = self.get_recipe_for(app)
        for k in source_recipe.keys():
            assert recipe[k] == source_recipe[k]


class ConfigRepository:
    def __init__(self):
        pass

    def create(self):
        if os.path.exists(REPO_NAME):
            shutil.rmtree(REPO_NAME)
        repo = git.Repo()
        repo.init(REPO_NAME, bare=True)

    def push_config(self, config_name='default'):
        repo = self.__checkout_repo()
        self.copy_config(config_name)
        repo.git.add('--all')
        repo.index.commit("updated by tests")
        repo.remote().push()

    def __checkout_repo(self):
        if os.path.exists(CHECKOUT_DIR):
            shutil.rmtree(CHECKOUT_DIR)
        return git.Repo.clone_from(GIT_REPO_URL, CHECKOUT_DIR)

    def copy_config(self, config_name):
        if not os.path.exists(os.path.dirname('behave_co/int/global.yml')):
            try:
                os.makedirs(os.path.dirname('behave_co/int/global.yml'))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        shutil.copyfile(LocalConfig(config_name).get_path(), 'behave_co/int/global.yml')


class LocalConfig:
    def __init__(self, name):
        self.name = name

    def content(self):
        return open(self.__get_config_path(), 'rb').read()

    def __get_config_path(self):
        return 'features/config/%s.yml' % self.name

    def get_path(self):
        return self.__get_config_path()

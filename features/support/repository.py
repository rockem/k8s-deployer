import os
import shutil

import git
import yaml

REPO_NAME = 'behave_repo'
GIT_REPO_URL = "file://" + os.getcwd() + '/' + REPO_NAME
CHECKOUT_DIR = 'co'


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



import errno
import os
import shutil
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


class SwaggerFileCreator(GitRepository):

    SWAGGER_YML_PATH = "out/swagger.yml"
    SWAGGER_YML_URL = "file://" + os.getcwd() + '/'+SWAGGER_YML_PATH

    def __init__(self):
        super(SwaggerFileCreator, self).__init__("swagger_repo", "swagger_co")

    def create_yml(self):
        FileCreator().create_for(self.SWAGGER_YML_PATH, yaml.load(open(os.path.join('features/config/swagger.yml'),"r")))

    def update_yml_with(self, value):
        self.__update_with(self.__read_content().replace('hello', value))

    def __update_with(self, content):
        with open(self.SWAGGER_YML_PATH, 'w') as f:
            f.write(content)

    def __read_content(self):
        with open(self.SWAGGER_YML_PATH, 'r') as file:
            file_data = file.read()
        return file_data



class RecipeRepository(GitRepository):
    REPO_NAME = 'recipe_repo'
    GIT_REPO_URL = "file://" + os.getcwd() + '/' + REPO_NAME
    CHECKOUT_DIR = 'recipe_co'
    RECIPE_PATH = CHECKOUT_DIR + "/int/services/recipe.yml"

    def __init__(self):
        super(RecipeRepository, self).__init__(self.REPO_NAME, self.CHECKOUT_DIR)

    def verify_app_is_logged(self, app):
        super(RecipeRepository, self)._checkout_repo()
        assert self.get_recipe_for(app)['image_name'] == app.image_name()

    def get_recipe_for(self, app):
        return yaml.load(open(os.path.join(self.CHECKOUT_DIR, 'int', 'services', '%s.yml' % app.service_name()), "r"))

    def log_app(self, app):
        repo = super(RecipeRepository, self)._checkout_repo()
        self.__create_recipe(app)
        repo.git.add('--all')
        repo.index.commit("updated by tests")
        repo.remote().push()
        self.__delete_recipe()

    def __delete_recipe(self):
        FileCreator.delete_from(self.RECIPE_PATH)

    def __create_recipe(self, app):
        FileCreator.create_for(self.RECIPE_PATH, {'image_name': app.image_name(), 'logging': 'none'})

    def verify_recipe_is_logged_for(self, app):
        super(RecipeRepository, self)._checkout_repo()
        source_recipe = yaml.load(open(app.recipe_path(), "r"))
        recipe = self.get_recipe_for(app)
        for k in source_recipe.keys():
            assert recipe[k] == source_recipe[k]


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
    GLOBAL_CONFIG_PATH = CHECKOUT_DIR + '/int/global.yml'
    JOBS_PATH = CHECKOUT_DIR + '/int/jobs.yml'

    def __init__(self):
        super(ConfigRepository, self).__init__(self.REPO_NAME, self.CHECKOUT_DIR)

    def push_job(self, job_config):
        config_dict = {job_config: self.JOBS_PATH,
                       "default": self.GLOBAL_CONFIG_PATH}
        self.__push(config_dict)

    def push_config(self, config_name):
        config_dict = {config_name: self.GLOBAL_CONFIG_PATH,
                       "jobs_default": self.JOBS_PATH}
        self.__push(config_dict)

    def __push(self, config_dict):
        repo = super(ConfigRepository, self)._checkout_repo()
        for source, target in config_dict.iteritems():
            self._copy(source, target)
        repo.git.add('--all')
        repo.index.commit("updated by tests")
        repo.remote().push()

    @staticmethod
    def _copy(source, target):
        if not os.path.exists(os.path.dirname(target)):
            try:
                os.makedirs(os.path.dirname(target))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        shutil.copyfile(LocalConfig(source).get_path(), target)


class LocalConfig:
    def __init__(self, name):
        self.name = name

    def content(self):
        return open(self.__get_config_path(), 'rb').read()

    def __get_config_path(self):
        return 'features/config/%s.yml' % self.name

    def get_path(self):
        return self.__get_config_path()

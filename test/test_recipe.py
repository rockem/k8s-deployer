import os

import errno
import yaml
from nose.tools.nontrivial import raises

from deployer.file import YamlReader
from deployer.recipe import Recipe, RecipeError


class TestRecipe():
    def __init__(self):
        self.TestRecipeUtil = RecipeFileCreator()

    def test_expose_should_be_true(self):
        assert Recipe.builder().ingredients({}).build().expose() is True

    def test_expose_should_be_delegated_from_file(self):
        self.generate_file_for({'expose': False})
        assert Recipe.builder().ingredients(self.read_recipe()).build().expose() is False

    def read_recipe(self):
        return YamlReader.read(RecipeFileCreator.RECIPE)

    def generate_file_for(self, dic):
        self.TestRecipeUtil.create_for(RecipeFileCreator.RECIPE, dic)

    @raises(RecipeError)
    def test_raise_value_error_when_non_bool_value(self):
        self.generate_file_for({'expose': 11})
        Recipe.builder().ingredients(self.read_recipe()).build().expose()

    def test_image_should_be_delegated_from_file(self):
        self.generate_file_for({'image_name': 'image_name'})
        assert Recipe.builder().ingredients(self.read_recipe()).build().image() == 'image_name'

    def test_props_should_delegated_from_file_and_builder(self):
        self.generate_file_for({'expose': False})
        recipe = Recipe.builder().ingredients(self.read_recipe()).image('image_name').build()
        assert recipe.image() == 'image_name'
        assert recipe.expose() is False

    def teardown(self):
        self.TestRecipeUtil.delete()


class RecipeFileCreator():
    RECIPE = './recipe.yml'

    def create_for(self, path, data):

        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

        with open(path, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

    def delete_from(self, path):
        try:
            os.remove(path)
        except OSError:
            print 'recipe path not found'

    def delete(self):
        try:
            os.remove(self.RECIPE)
        except OSError:
            print 'recipe path not found'

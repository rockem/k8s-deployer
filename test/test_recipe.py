import os

import yaml
from nose.tools.nontrivial import raises

from deployer.recipe import Recipe


class TestRecipe():
    def __init__(self):
        self.TestRecipeUtil = RecipeFileCreator()

    def test_expose_should_be_true(self):
        assert Recipe.builder().build().expose() is True

    def test_expose_should_be_delegated_from_file(self):
        self.generate_file_for({'expose': False})
        assert Recipe.builder().indgredients(RecipeFileCreator.RECIPE).build().expose() is False

    def generate_file_for(self, dic):
        self.TestRecipeUtil.create_for(RecipeFileCreator.RECIPE, dic)

    @raises(ValueError)
    def test_raise_value_error_when_non_bool_value(self):
        self.generate_file_for({'expose': 11})
        Recipe.builder().indgredients(RecipeFileCreator.RECIPE).build().expose()

    def test_image_should_be_delegeted_from_file(self):
        self.generate_file_for({'image_name': 'image_name'})
        assert Recipe.builder().indgredients(RecipeFileCreator.RECIPE).build().image() == 'image_name'

    def test_props_should_delegated_from_file_and_builder(self):
        self.generate_file_for({'expose': False})
        recipe = Recipe.builder().indgredients(RecipeFileCreator.RECIPE).image('image_name').build()
        assert recipe.image() == 'image_name'
        assert recipe.expose() is False

    def tearDown(self):
        self.TestRecipeUtil.delete()


class RecipeFileCreator():
    RECIPE = './recipe.yml'

    def create_for(self, path, data):
        with open(path, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

    def delete(self):
        try:
            os.remove(self.RECIPE)
        except OSError:
            print 'recipe path not found'

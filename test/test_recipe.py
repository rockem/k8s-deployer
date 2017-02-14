import os

import yaml
from nose.tools.nontrivial import raises

from deployer.recipe import Recipe, RecipeExtractor


class TestRecipeExtractor():

    def test_should_return_true(self):
        assert RecipeExtractor().extract('true') == True

    def test_should_return_true_ignore_value_case(self):
        assert RecipeExtractor().extract('TRUE') == True

class TestRecipe():

    def __init__(self):
        self.TestRecipeUtil = RecipeFileCreator()

    def test_expose_default_given__fake_path(self):
        assert Recipe('not_real_path').expose() == True

    def test_expose_should_fetched_from_file(self):
        self.generate_file_for({'expose': 'false'})
        assert Recipe(RecipeFileCreator.RECIPE).expose() == False

    def generate_file_for(self, dic):
        self.TestRecipeUtil.create_for(RecipeFileCreator.RECIPE, dic)

    @raises(ValueError)
    def test_raise_value_error_when_non_bool_value(self):
        self.generate_file_for({'expose': 11})
        Recipe(RecipeFileCreator.RECIPE).expose()

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
        except OSError as e:
            print 'recipe path not found'

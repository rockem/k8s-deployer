from nose.tools.nontrivial import raises

from deployer.recipe import Recipe, RecipeError


class TestRecipe(object):
    def test_expose_should_be_true(self):
        assert Recipe.builder().ingredients({}).build().expose() is True

    def test_expose_should_be_delegated_from_file(self):
        assert Recipe.builder().ingredients({'expose': False}).build().expose() is False

    @raises(RecipeError)
    def test_raise_value_error_when_non_bool_value(self):
        Recipe.builder().ingredients({'expose': 11}).build().expose()

    def test_image_should_be_delegated_from_ingredients(self):
        assert Recipe.builder().ingredients({'image_name': 'kuku'}).build().image() == 'kuku'

    def test_props_should_delegated_builder(self):
        recipe = Recipe.builder().ingredients({'expose': False}).image('popov').build()
        assert recipe.image() == 'popov'
        assert recipe.expose() is False

    def test_service_type_should_be_delegated_from_ingredients(self):
        recipe = Recipe.builder().ingredients({'service_type': Recipe.SERVICE_TYPE_UI}).build()
        assert recipe.service_type() is Recipe.SERVICE_TYPE_UI

    def test_service_type_should_be_api_by_default(self):
        recipe = Recipe.builder().ingredients({}).build()
        assert recipe.service_type() is Recipe.SERVICE_TYPE_API

    def test_ports_should_delegate_from_ingredients(self):
        recipe = Recipe.builder().ingredients({'ports': [{'name': 'kuku'}]}).build()
        assert recipe.ports()[0]['name'] == 'kuku'

    def test_empty_ports_list_as_default(self):
        assert Recipe.builder().build().ports() == []

    def test_metrics_should_be_disabled_by_default(self):
        recipe = Recipe.builder().build()
        assert recipe.metrics()['enabled'] is False

    def test_metrics_should_be_delegated_from_ingredients(self):
        recipe = Recipe.builder().ingredients({'metrics': {'enabled': True}}).build()
        assert recipe.metrics()['enabled'] is True

    def test_admin_privileges_should_be_disabled_by_default(self):
        recipe = Recipe.builder().build()
        assert recipe.admin_privileges()['enabled'] is False

    def test_admin_privileges_should_be_delegated_from_ingredients(self):
        recipe = Recipe.builder().ingredients({'adminPrivileges': {'enabled': True}}).build()
        assert recipe.admin_privileges()['enabled'] is True

    def test_autoscale_should_be_disabled_by_default(self):
        recipe = Recipe.builder().build()
        assert recipe.autoscale()['enabled'] is False

    def test_autoscale_should_be_delegate_from_ingredients(self):
        recipe = Recipe.builder().ingredients({'autoscale': {'enabled': True, 'cpu': 'low' }}).build()
        assert recipe.autoscale()['enabled'] is True
        assert recipe.autoscale()['cpu'] is 'low'

import os
import time

from nose.tools import raises
from pymongo import MongoClient

from deployer.repository import MongoDeploymentRepository, NotEnoughDeployments


class TestMongoConnectorIT:

    def __init__(self):
        uri = 'mongodb://{0}:27017/deployer'.format(os.getenv('MONGO_HOST', 'localhost'))
        self.connector = MongoDeploymentRepository(uri)
        self.client = MongoClient(uri)
        self.collection_name = self.connector.COLLECTION

        time_now = int(round(time.time() * 1000))

        self.OLD_WIZARD = {"service_name": "wizard", "env": "int", "timestamp": time_now, "rolled_back": False,
                           "recipe": {"expose": "true", "image_name": "wizard:123", "logging": "log4j", "ports": "[]",
                                      "service_type": "api"}}

        self.OLD_WIZARD_WITH_GREATER_TIME = {"service_name": "wizard", "env": "int", "timestamp": time_now + 100,
                                             "rolled_back": False,
                                             "recipe": {"expose": "true", "image_name": "wizard:123",
                                                        "logging": "log4j", "ports": "[]",
                                                        "service_type": "api"}}

        self.NEW_WIZARD = {"service_name": "wizard", "env": "int", "timestamp": time_now + 100, "rolled_back": False,
                           "recipe": {"expose": "true", "image_name": "wizard:456", "logging": "log4j", "ports": "[]",
                                      "service_type": "api"}}

        self.NEW_WIZARD_STG = {"service_name": "wizard", "env": "stg", "timestamp": time_now + 100,
                               "rolled_back": False,
                               "recipe": {"expose": "true", "image_name": "wizard:456", "logging": "log4j",
                                          "ports": "[]",
                                          "service_type": "api"}}

        self.NEW_WIZARD_ROLLED_BACK = {"service_name": "wizard", "env": "int", "timestamp": time_now + 100,
                                       "rolled_back": True,
                                       "recipe": {"expose": "true", "image_name": "wizard:456", "logging": "log4j",
                                                  "ports": "[]",
                                                  "service_type": "api"}}

        self.OLD_MAGNIFICENT = {"service_name": "magnificent", "env": "int", "timestamp": time_now - 100,
                                "rolled_back": False,
                                "recipe": {"expose": "true", "image_name": "magnificent:456", "logging": "log4j",
                                           "ports": "[]",
                                           "service_type": "api"}}

        self.NEW_MAGNIFICENT = {"service_name": "magnificent", "env": "int", "timestamp": time_now + 100,
                                "rolled_back": False,
                                "recipe": {"expose": "true", "image_name": "magnificent:456", "logging": "log4j",
                                           "ports": "[]",
                                           "service_type": "api"}}

    def setup(self):
        self.connector.clean_all_docs_from_default()

    def test_write_deployment(self):
        self.connector.write_deployment(self.OLD_WIZARD)

        lst = self.create_list_from_cursor(self.client.get_database()[self.collection_name].find({}))

        self.assert_lst_size(lst, 1)

        assert any(item['service_name'] == 'wizard'
                   and item['env'] == 'int'
                   and item['recipe']['image_name'] == 'wizard:123' for item in lst)

    def test_dont_write_new_deployment_if_exist_image_name(self):
        self.connector.write_deployment(self.OLD_WIZARD)
        self.connector.write_deployment(self.OLD_WIZARD_WITH_GREATER_TIME)

        collection = self.client.get_database()[self.collection_name]
        new_lst = self.create_list_from_cursor(collection.find({}))
        self.assert_lst_size(new_lst, 1)

        assert any(item['timestamp'] == self.OLD_WIZARD['timestamp'] for item in new_lst)

    def test_should_get_only_top_recipes(self):
        self.connector.write_deployment(self.OLD_WIZARD)
        self.connector.write_deployment(self.NEW_WIZARD)
        self.connector.write_deployment(self.NEW_MAGNIFICENT)

        recipes = self.connector.get_all_recipes("int")

        self.assert_lst_size(recipes, 2)

        self.assert_image_exist(self.NEW_WIZARD['recipe']['image_name'], recipes)
        self.assert_image_exist(self.NEW_MAGNIFICENT['recipe']['image_name'], recipes)

    def test_should_get_only_from_env(self):
        self.connector.write_deployment(self.NEW_MAGNIFICENT)
        self.connector.write_deployment(self.NEW_WIZARD_STG)

        recipes = self.connector.get_all_recipes("int")

        self.assert_lst_size(recipes, 1)
        self.assert_image_exist(self.NEW_MAGNIFICENT['recipe']['image_name'], recipes)

    def assert_image_exist(self, image_name, recipes):
        assert any(item['image_name'] == image_name for item in recipes)

    def test_should_not_get_rolled_back_service(self):
        self.connector.write_deployment(self.NEW_WIZARD_ROLLED_BACK)
        self.connector.write_deployment(self.NEW_MAGNIFICENT)

        recipes = self.connector.get_all_recipes("int")
        self.assert_lst_size(recipes, 1)

        self.assert_image_exist(self.NEW_MAGNIFICENT['recipe']['image_name'], recipes)

    def test_should_take_only_the_top(self):
        self.connector.write_deployment(self.OLD_WIZARD)
        self.connector.write_deployment(self.NEW_WIZARD)

        recipes = self.connector.get_all_recipes("int")
        self.assert_lst_size(recipes, 1)

        self.assert_image_exist(self.NEW_WIZARD['recipe']['image_name'], recipes)

    def test_should_update_as_rolledback(self):
        self.connector.write_deployment(self.OLD_WIZARD)
        self.connector.write_deployment(self.NEW_WIZARD)

        self.connector.rollback("wizard", "int")
        obj = self.client.get_database()[self.collection_name].find_one({'recipe.image_name': "wizard:456"})
        assert obj['rolled_back'] is True

    def test_should_get_previous_deployment_of_service(self):
        self.connector.write_deployment(self.OLD_WIZARD)
        self.connector.write_deployment(self.NEW_WIZARD)
        previous_deployment = self.connector.get_previous_deployment("wizard", "int")

        assert previous_deployment['recipe']['image_name'] == self.OLD_WIZARD['recipe']['image_name']

    @raises(NotEnoughDeployments)
    def test_should_fail_when_not_enough_deployments(self):
        self.connector.write_deployment(self.OLD_WIZARD)

        self.connector.get_previous_deployment("wizard", "int")

    def test_should_get_deployments_greater_then_time(self):
        self.connector.write_deployment(self.OLD_WIZARD)
        self.connector.write_deployment(self.NEW_WIZARD)
        self.connector.write_deployment(self.NEW_MAGNIFICENT)

        lst = self.connector.get_all_deployment_from_time("int", self.OLD_WIZARD['timestamp'], "wizard")

        self.assert_lst_size(lst, 1)

        assert lst[0]['recipe']['image_name'] == self.NEW_MAGNIFICENT['recipe']['image_name']

    @staticmethod
    def create_list_from_cursor(lst):
        new_lst = []
        for doc in lst:
            new_lst.append(doc)
        return new_lst

    def assert_lst_size(self, lst, size):
        assert len(lst) == size

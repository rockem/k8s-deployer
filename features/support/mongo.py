import time

import yaml
from pymongo import MongoClient


class MongoDriver:

    COLLECTION = 'deployments'

    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.collection = self.client.get_database()[self.COLLECTION]

    def clean(self):
        self.collection.remove({})

    def verify_app_is_logged(self, app):
        image_name = app.image_name()
        assert self.collection.find_one({"recipe.image_name": image_name}) is not None

    def verify_recipe_is_logged_for(self, app):
        expected_recipe = yaml.load(open(app.recipe_path(), "r"))
        recipe_from_mongo = self.collection.find_one({"recipe.image_name": app.image_name()})['recipe']
        for k in expected_recipe.keys():
            assert expected_recipe[k] == recipe_from_mongo[k]

    def write_deployment(self, service_name, env, recipe_data):
        self.collection.insert({"service_name": service_name,
                                "timestamp": int(round(time.time() * 1000)),
                                "env": env,
                                "recipe": recipe_data,
                                "rolled_back": False})
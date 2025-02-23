import pymongo
from pymongo import MongoClient


class MongoDeploymentRepository:
    COLLECTION = 'deployments'

    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.collection = self.client.get_database()[self.COLLECTION]

    def write_deployment(self, deployment):
        image_name = deployment['recipe']['image_name']
        if(self.not_have_element(
                self.collection.find(
                    self.__combine_filters(
                        self.__eq_env(deployment["env"]),
                        self.__eq_service_name(deployment["service_name"]),
                        self.__eq_image_name(image_name),
                        self.__not_rolled_back())))):
            self.collection.insert_one(deployment)

    def not_have_element(self, res):
        return res.count() == 0

    def __eq_image_name(self, image_name):
        return {"recipe.image_name": {"$eq": image_name}}

    def get_previous_deployment(self, service_name, env):
        return self.get_the_n_newest_service_deployment(service_name, env, 1)

    def get_current_deployment(self, service_name, env):
        return self.get_the_n_newest_service_deployment(service_name, env)

    def get_the_n_newest_service_deployment(self, service_name, env, n=0):
        return self.cursor_to_obj(
            self.collection.find(
                self.__combine_filters(
                    self.__eq_env(env),
                    self.__eq_service_name(service_name),
                    self.__not_rolled_back()))
                .sort("timestamp", pymongo.DESCENDING).skip(n).limit(1))

    def get_all_deployment_from_time(self, env, timestamp, service_name):
        return self.create_list_from_cursor(
            self.collection.find(
                self.__combine_filters(
                    self.__eq_env(env),
                    self.__not_rolled_back(),
                    self.__greater_then(timestamp),
                    self.__not_eq_service_name(service_name)))
                .sort("timestamp", pymongo.DESCENDING))

    def __greater_then(self, timestamp):
        return {"timestamp": {"$gt": timestamp}}

    def __eq_env(self, env):
        return {"env": {"$eq": env}}

    def __not_rolled_back(self):
        return {"rolled_back": {"$ne": True}}

    def __eq_service_name(self, service_name):
        return {"service_name": {"$eq": service_name}}

    def __not_eq_service_name(self, service_name):
        return {"service_name": {"$ne": service_name}}

    def rollback(self, service_name, env):
        self.collection.find_one_and_update(
            self.__combine_filters(
                self.__eq_env(env),
                self.__eq_service_name(service_name),
                self.__not_rolled_back()
            ),
            {'$set': {'rolled_back': True}},
            sort=[('timestamp', pymongo.DESCENDING)])

    def get_all_recipes(self, env):
        return self.create_recipe_list_from_cursor(self.collection.aggregate(
            [
                {"$match": {"rolled_back": False}},
                {"$match": {"env": env}},
                {"$sort": {"timestamp": -1}},
                {"$group": {"_id": "$service_name", "recipe": {"$first": "$recipe"}}}
            ]
        ))

    def cursor_to_obj(self, cursor):
        lst = self.create_list_from_cursor(cursor)
        self.check_if_lst_is_empty(lst)
        return lst[0]

    def check_if_lst_is_empty(self, lst):
        if len(lst) == 0:
            raise NotEnoughDeployments

    def __combine_filters(self, *filters):
        filter_dict = {}
        for _filter in filters:
            filter_dict.update(_filter)
        return filter_dict

    def clean_all_docs_from_default(self):
        self.collection.remove({})

    @staticmethod
    def create_list_from_cursor(cursor):
        new_lst = []
        for doc in cursor:
            new_lst.append(doc)
        return new_lst

    def fail_if_not_enough_elements(self, lst):
        if len(lst) < 2:
            raise NotEnoughDeployments

    def create_recipe_list_from_cursor(self, cursor):
        new_lst = []
        for doc in cursor:
            new_lst.append(doc['recipe'])
        return new_lst


class NotEnoughDeployments(Exception):
    def __init(self, message):
        super(NotEnoughDeployments, self).__init__(message)


class DummyMongoConnector:
    def __init__(self):
        pass

    def write_deployment(self, deploy_log):
        pass

    def get_previous_deployment(self, service_name, env):
        return {}

    def get_all_deployment_from_time(self, env, timestamp, service_name):
        return {}

    def rollback(self, service_name, env):
        pass

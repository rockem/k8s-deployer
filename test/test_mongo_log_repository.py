import time

from nose.tools import raises

from deployer.protected_rollback_proxy import ProtectedRollbackProxy, NotLatestDeployment


class MongoConnectorStub:
    def __init__(self):
        self.deployments = []
        self.deployment_number = 0

    def get_current_deployment(self, service_name, env):
        return self.get_service_deployments_sorted(service_name, env)[0]

    def get_previous_deployment(self, service_name, env):
        lst = self.get_service_deployments_sorted(service_name, env)
        return lst[1]

    def get_all_deployment_from_time(self, env, timestamp, service_name):
        lst = self.get_all_deployments_sorted_by_timestamp_desc(env)
        return filter(lambda elem: elem['timestamp'] > timestamp and  elem['service_name'] != service_name, lst)

    def update_as_rolldback(self, mongo_id):
        for deployment in self.deployments:
            if deployment['_id'] == mongo_id:
                deployment['rolled_back'] = True

    def write_deployment(self, obj):
        combined = obj.copy()
        self.deployment_number += 1
        combined.update({"_id": self.deployment_number, "rolled_back": False})
        self.deployments.append(combined)

    def get_service_deployments_sorted(self, service_name, env):
        lst = []
        for service in self.deployments:
            if service['service_name'] == service_name and service['env'] == env:
                lst.append(service)

        return self.sort_reverse_by_timestamp(lst)

    def get_all_deployments_sorted_by_timestamp_desc(self, env):

        return self.sort_reverse_by_timestamp(self.deployments)

    @staticmethod
    def sort_reverse_by_timestamp(lst):
        def get_timestamp(elem): return elem['timestamp']

        return sorted(lst, key=get_timestamp, reverse=True)


class TestDeployMongoRepository(object):
    TARGET = "int"
    time_now = int(round(time.time() * 1000))

    OLD_WIZARD_DEPLOYMENT = {"service_name": "wizard", "env": "int", "timestamp": time_now,
                             "recipe": {"expose": "true", "image_name": "wizard:456", "logging": "log4j", "ports": "[]",
                                        "service_type": "api"}}
    VERY_OLD_WIZARD_DEPLOYMENT = {"service_name": "wizard", "env": "int", "timestamp": time_now - 1000,
                                  "recipe": {"expose": "true", "image_name": "wizard:123", "logging": "log4j", "ports": "[]",
                                             "service_type": "api"}}

    NEW_WIZARD_DEPLOYMENT = {"service_name": "wizard", "env": "int", "timestamp": time_now + 1000,
                             "recipe": {"expose": "true", "image_name": "wizard:789", "logging": "log4j", "ports": "[]",
                                        "service_type": "api"}}

    OLD_MAGNIFICENT_DEPLOYMENT = {"service_name": "magnificent", "env": "int", "timestamp": time_now,
                                  "recipe": {"expose": "true", "image_name": "magnificent:123", "logging": "log4j", "ports": "[]",
                                             "service_type": "api"}}

    NEW_MAGNIFICENT_DEPLOYMENT = {"service_name": "magnificent", "env": "int", "timestamp": time_now + 1000,
                                  "recipe": {"expose": "true", "image_name": "magnificent:456", "logging": "log4j", "ports": "[]",
                                             "service_type": "api"}}

    def __init__(self):
        self.mongo_connector = None

    def setup(self):
        self.mongo_connector = MongoConnectorStub()

    def test_should_write_to_mongo(self):
        repository = ProtectedRollbackProxy(self.mongo_connector, 'int', "wizard")
        recipe = {"expose": "true", "image_name": "wizard:123", "logging": "log4j", "ports": "[]",
                  "service_type": "api"}
        repository.write_deployment(recipe)

        deployments = self.mongo_connector.get_service_deployments_sorted("wizard", "int")

        assert len(deployments) == 1

        assert any(deployment['service_name'] == "wizard" and
                   deployment['env'] == 'int' and
                   deployment['recipe']['service_type'] == 'api' and
                   deployment['recipe']['image_name'] == 'wizard:123' for deployment in deployments)

    @raises(NotLatestDeployment)
    def test_should_fail_when_newer_deployment_exist(self):

        repository_wizard = ProtectedRollbackProxy(self.mongo_connector, 'int', "wizard")
        repository_magnificent = ProtectedRollbackProxy(self.mongo_connector, 'int', "magnificent")

        repository_wizard.write_deployment(self.VERY_OLD_WIZARD_DEPLOYMENT['recipe'])
        time.sleep(1)
        repository_wizard.write_deployment(self.OLD_WIZARD_DEPLOYMENT['recipe'])
        time.sleep(1)
        repository_magnificent.write_deployment(self.NEW_MAGNIFICENT_DEPLOYMENT['recipe'])

        repository_wizard.get_previous_recipe()



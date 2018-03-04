import getpass
import json
import subprocess
import time
import unittest

from deployer import k8s
from deployer.k8s import K8sConnector
from deployer.recipe import RecipeBuilder, Recipe


class TestConnectorIt:
    __namespace = ""
    __connector = None

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        cls.__namespace = cls.__create_arbitrary_namespace_name()
        cls.__create_namespace()
        cls.__connector = K8sConnector(cls.__namespace)

    @classmethod
    def __create_arbitrary_namespace_name(cls):
        return getpass.getuser() + "-" + str(int(time.time()))

    @classmethod
    def teardown_class(cls):
        cls._delete_namespace()

    @classmethod
    def __create_namespace(cls):
        subprocess.check_output('kubectl create namespace %s' % cls.__namespace, shell=True)

    @classmethod
    def _delete_namespace(cls):
        subprocess.call("kubectl delete namespace %s" % cls.__namespace, shell=True)

    @unittest.skip("not in use")
    def test_modify_job_successfully(self):
        job = {'name': 'job1', 'schedule': '*/1 * * * *', 'url': 'job1/run'}

        self.__connector.upload_job(job)
        self.__modify_job(job, 'some_other_url')

        assert self._retrieve_url_of(job['name']) == 'some_other_url'

    def __modify_job(self, job, modified_url):
        job['url'] = modified_url
        self.__connector.upload_job(job)

    def _retrieve_url_of(self, job_name):
        output = subprocess.check_output("kubectl --namespace %s get cronjob %s -o json" % (self.__namespace, job_name),
                                         shell=True)
        job_as_josn = json.loads(output)
        return self.__extract_job_url_from(job_as_josn)

    def __extract_job_url_from(self, job_as_josn):
        return job_as_josn['spec']['jobTemplate']['spec']['template']['spec']['containers'][0]['args'][1]

    def test_service_should_not_recreated_when_same_type(self):
        properties = self._create_service(Recipe.SERVICE_TYPE_UI)
        uuid = self.__service_uuid(properties['serviceName'])
        self._create_service(Recipe.SERVICE_TYPE_UI)
        assert self.__service_uuid(properties['serviceName']) == uuid

    def test_modify_service_type(self):
        assert self._created_service_with_type(Recipe.SERVICE_TYPE_UI) == k8s.LOAD_BALANCER_SERVICE
        assert self._created_service_with_type(Recipe.SERVICE_TYPE_API) == k8s.CLUSTER_IP_SERVICE

    def _created_service_with_type(self, service_type):
        properties = self._create_service(service_type)
        return self.__service_type(properties['serviceName'])

    def _create_service(self, service_type):
        properties = self.__create_properties_with(service_type)
        self.__connector.apply_service(properties)
        return properties

    def __service_uuid(self, service_name):
        loads = self.__connector.describe_service(service_name)
        return loads['metadata']['uid']

    def __service_type(self, service_name):
        return self.__connector.describe_service(service_name)['spec']['type']

    def __create_properties_with(self, service_type):
        recipe = RecipeBuilder().image("dummy-image").ingredients({'service_type':service_type}).build()
        return {
            'env': 'int',
            'name': 'dummy-deployment',
            'scale': 1,
            'serviceName': 'dummy-service',
            'image': 'dummy-image',
            'podColor': 'green',
            'serviceColor': 'green',
            'myEnv': 'int',
            'logging': recipe.logging(),
            'ports': recipe.ports(),
            'domain': 'heed-dev.io',
            'serviceType': recipe.service_type()
        }

    def test_scale_deployment(self):
        properties = self.create_api_type_deployment()

        deployment_name = properties['name']
        self.__connector.scale_deployment(deployment_name, 0)
        assert self._deployment_scale(deployment_name) == 0

    def test_describe_deployment(self):
        properties = self.create_api_type_deployment()

        deployment_name = properties['name']
        deployment_description = self.__connector.describe_deployment(deployment_name)
        assert deployment_description['metadata']['name'] == deployment_name

    def create_api_type_deployment(self):
        properties = self.__create_properties_with(Recipe.SERVICE_TYPE_API)
        self.__connector.apply_deployment(properties)
        return properties


    def _deployment_scale(self, deployment_name):
        deployment = subprocess.check_output("kubectl --namespace %s get deployment %s -o json"
                                             % (self.__namespace, deployment_name), shell=True)
        return json.loads(deployment)['spec']['replicas']
import getpass
import json
import subprocess

import time

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


    def test_modify_service_type(self):
        service_name = 'dummy-service'

        assert self.__service_created_type(service_name, Recipe.SERVICE_TYPE_UI) == k8s.LOAD_BALANCER_SERVICE
        assert self.__service_created_type(service_name, Recipe.SERVICE_TYPE_API) == k8s.CLUSTER_IP_SERVICE

    def __service_created_type(self, service_name, service_type):
        properties = self.__create_properties_with(service_name, service_type)
        self.__connector.apply_service(properties)
        return self.__service_type(service_name)

    def __service_type(self, service_name):
        return json.loads(self.__connector.get_service_as_json(service_name))['spec']['type']

    def __create_properties_with(self, service_name, service_type):
        recipe = RecipeBuilder().image("dummy-image").ingredients({'service_type':service_type}).build()
        return {
            'env': 'int',
            'name': service_name,
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
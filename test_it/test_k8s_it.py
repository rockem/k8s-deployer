import getpass
import json
import subprocess

import time

from deployer.k8s import Connector

class TestConnectorIt:
    _namespace = ""

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        cls._namespace = cls.__create_arbitrary_namespace_name()
        cls.__create_namespace()

    @classmethod
    def __create_arbitrary_namespace_name(cls):
        return getpass.getuser() + "-" + str(int(time.time()))

    @classmethod
    def teardown_class(cls):
        cls._delete_namespace()

    @classmethod
    def __create_namespace(cls):
        subprocess.check_output('kubectl create namespace %s' % cls._namespace, shell=True)

    @classmethod
    def __create_connector(cls):
        cls._connector = Connector(cls._namespace)

    @classmethod
    def _delete_namespace(cls):
        subprocess.call("kubectl delete namespace %s" % cls._namespace, shell=True)

    def test_modify_job_successfully(self):
        connector = Connector(self._namespace)
        job = {'name': 'job1', 'schedule': '*/1 * * * *', 'url': 'job1/run'}

        connector.upload_job(job)
        self.__modify_job(connector, job, 'some_other_url')

        assert self._retrieve_url_of(job['name']) == 'some_other_url'

    def __modify_job(self, connector, job, modified_url):
        job['url'] = modified_url
        connector.upload_job(job)

    def _retrieve_url_of(self, job_name):
        output = subprocess.check_output("kubectl --namespace %s get cronjob %s -o json" % (self._namespace, job_name),
                                         shell=True)
        job_as_josn = json.loads(output)
        return self.__extract_job_url_from(job_as_josn)

    def __extract_job_url_from(self, job_as_josn):
        return job_as_josn['spec']['jobTemplate']['spec']['template']['spec']['containers'][0]['args'][1]

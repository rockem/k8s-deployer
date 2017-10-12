import boto3 as boto3
import time

from log import DeployerLogger
from util import EnvironmentVariablesFetcher
from yml import SwaggerFileReader

client = boto3.client('apigateway')

logger = DeployerLogger('deployer').getLogger()


class ApiGatewayConnector(object):
    def __init__(self):
        self.rest_api_id = EnvironmentVariablesFetcher().fetch("REST_API_ID")
        self.target_env = EnvironmentVariablesFetcher().fetch("TARGET_ENV")


    def __upload_swagger(self, yml_path):
        client.put_rest_api(restApiId=self.rest_api_id, mode='overwrite', failOnWarnings=False,
                            body=SwaggerFileReader(yml_path).read())
        client.create_deployment(restApiId=self.rest_api_id,
                                 stageName=self.target_env, cacheClusterEnabled=False)


    def upload_swagger(self, yml_path):
        self.__busy_wait(self.__upload_swagger(yml_path))

    def __busy_wait(self, run_func, *args):
        result = False
        for _ in range(20):
            logger.debug('try # %s' % _)
            try:
                if run_func(args[0]):
                    result = True
                    break
            except Exception:
                pass
            time.sleep(1)

        return result
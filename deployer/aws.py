import subprocess

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

    def upload_swagger(self, yml_path):
        client.put_rest_api(restApiId=self.rest_api_id, mode='overwrite', failOnWarnings=False, body=SwaggerFileReader(yml_path).read())
        client.create_deployment(restApiId=self.rest_api_id, stageName=self.target_env, cacheClusterEnabled=False)

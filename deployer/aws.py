import time

import boto3 as boto3

from log import DeployerLogger
from util import EnvironmentVariablesFetcher
from yml import SwaggerFileReader

logger = DeployerLogger('deployer').getLogger()


class ApiGatewayConnector(object):
    def __init__(self):
        self.rest_api_id = EnvironmentVariablesFetcher().fetch("REST_API_ID")
        self.target_env = EnvironmentVariablesFetcher().fetch("TARGET_ENV")

    def upload_swagger(self, yml_path):
        apigateway_client = boto3.client('apigateway')
        apigateway_client.put_rest_api(restApiId=self.rest_api_id, mode='overwrite', failOnWarnings=False,
                                       body=SwaggerFileReader(yml_path).read())
        for i in range(0, 5):
            try:
                apigateway_client.create_deployment(restApiId=self.rest_api_id, stageName=self.target_env,
                                                    cacheClusterEnabled=False)
                break
            except Exception as e:
                time.sleep(2 * i + 1)
                if i == 4:
                    raise e


class AwsConnector(object):
    def get_certificate_for(self, domain):
        acm_client = boto3.client('acm')
        certificates = acm_client.list_certificates()
        return next((certificate['CertificateArn']
                     for certificate in certificates['CertificateSummaryList']
                     if certificate['DomainName'] == domain), None)

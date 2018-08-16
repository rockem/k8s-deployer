import time

import boto3 as boto3

from log import DeployerLogger

logger = DeployerLogger('deployer').getLogger()

class AwsConnector(object):
    def get_certificate_for(self, domain):
        acm_client = boto3.client('acm')
        certificates = acm_client.list_certificates()
        return next((certificate['CertificateArn']
                     for certificate in certificates['CertificateSummaryList']
                     if certificate['DomainName'] == domain), None)

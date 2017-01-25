from time import sleep

import requests
import subprocess
from behave import then
from deployer.log import DeployerLogger
from requests.exceptions import ConnectionError
from support import NAMESPACE, JAVA_SERVICE_NAME, __busy_wait

logger = DeployerLogger(__name__).getLogger()


@then("the service should get the new configuration")
def get_configuration(context):
    logger.debug('waiting for the service deployment')
    svc_host = __busy_wait(__get_svc_host)
    greeting = __get_greeting(svc_host, '/greeting')
    assert greeting == 'Hello overridden world'


def __get_svc_host():
    service_describe_output = ''
    try:
        service_describe_output = subprocess.check_output("kubectl describe --namespace %s service %s" % (NAMESPACE, JAVA_SERVICE_NAME), shell=True)
    except Exception as e:
        sleep(1)
    # e.g. LoadBalancer Ingress:	a31d2dc35d67311e6b4410e7feeb8c22-467957310.us-east-1.elb.amazonaws.com
    #      Port:			        <unset>	80/TCP
    lb_index = service_describe_output.find("LoadBalancer Ingress:")
    if lb_index == -1:
        sleep(1)
        raise ConnectionError
    svc_host = service_describe_output[lb_index+22:service_describe_output.find("Port")-1]
    __call_service(svc_host)
    return svc_host


def __call_service(svc_host):
    url = 'http://' + svc_host + '/health'
    health = requests.get(url).text
    logger.info('The service url is:%s, \nThe returned health is:%s' % (url, health))


def __get_greeting(svc_host, path):
    url = 'http://' + svc_host + path
    return requests.get(url).text

from time import sleep

import requests
import subprocess
from behave import then
from deployer.log import DeployerLogger
from requests.exceptions import ConnectionError
from support import NAMESPACE, JAVA_SERVICE_NAME

logger = DeployerLogger(__name__).getLogger()


@then("the service should get the new configuration")
def get_configuration(context):
    logger.debug('waiting for the service deployment')
    svc_host = __wait_for_service_deploy()
    greeting = __get_greeting(svc_host, '/greeting')
    assert greeting == 'Hello overridden world'


def __wait_for_service_deploy():
    svc_host = None
    for _ in range(120):
        try:
            service_describe_output = subprocess.check_output("kubectl describe --namespace %s service %s" %
                                                              (NAMESPACE, JAVA_SERVICE_NAME), shell=True)
            # e.g. LoadBalancer Ingress:	a31d2dc35d67311e6b4410e7feeb8c22-467957310.us-east-1.elb.amazonaws.com
            #      Port:			        <unset>	80/TCP
            lb_index = service_describe_output.find("LoadBalancer Ingress:")
            if lb_index == -1:
                sleep(1)
                continue
            svc_host = service_describe_output[lb_index + 22:service_describe_output.find("Port") - 1]
            __call_service(svc_host)
            break
        except ConnectionError:
            sleep(1)
    if svc_host is None:
        raise Exception('The service did not start after 120 seconds')
    return svc_host


def __call_service(svc_host):
    url = 'http://' + svc_host + '/health'
    health = requests.get(url).text
    logger.info('The service url is:%s, \nThe returned health is:%s' % (url, health))


def __get_greeting(svc_host, path):
    url = 'http://' + svc_host + path
    return requests.get(url).text

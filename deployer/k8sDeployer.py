import os

from configuration_generator import ConfigGenerator, ConfigAppender
from log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()

#
# class K8sNotAvailableError(Exception):
#     K8S_NOT_RESPONDING_MSG = "k8s is not responding to ping"
#
#     def __init(self):
#         super(K8sNotAvailableError, self).__init__(self.K8S_NOT_RESPONDING_MSG)
#
# #
# class K8sDeployer(object):
#     def __init__(self, connector):
#         self.connector = connector
#         print "init K8sDeployer!"
#
#     def deploy(self,target):
#         source_to_deploy = os.path.join('deployer/produce/' + "%s.yml" % target)
#         self.connector.cluster_info()
#         logger.debug("going to deploy {}".format(source_to_deploy))
#         self.connector.apply(source_to_deploy)
#
#

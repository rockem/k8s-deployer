import getpass
import os
import subprocess
import time

from kubectlconf.s3 import S3Sync

from deployer.log import DeployerLogger
from features.support.context import Context
from features.support.docker import AppImageBuilder, JavaAppBuilder, AWSImagePusher
from features.support.k8s import K8sDriver
from features.support.repository import RecipeRepository, ConfigRepository

TARGET_ENV = 'int'

logger = DeployerLogger(__name__).getLogger()

APP_BUILDERS = [
    AppImageBuilder('version', 'healthy', ['VERSION=healthy']),
    AppImageBuilder('version', 'sick', ['VERSION=sick']),
    AppImageBuilder('restless', '1.0'),
    JavaAppBuilder(AppImageBuilder('java', '1.0')),
    AppImageBuilder('version', '1.0', ['VERSION=1.0']),
    AppImageBuilder('version', '2.0', ['VERSION=2.0'])
]


def before_all(context):
    __build_apps(context)
    os.environ['TARGET_ENV'] = TARGET_ENV
    if __is_aws_mode(context):
        os.system('kubectl-conf ')
        S3Sync(TARGET_ENV).sync()
        context.aws_uri = "911479539546.dkr.ecr.us-east-1.amazonaws.com/"
        context.minikube = None
        __push_apps_aws(Context(context).all_apps())
    else:
        context.minikube = subprocess.check_output('minikube ip', shell=True)[:-1]
        context.aws_uri = ''


def __build_apps(context):
    for b in APP_BUILDERS:
        app = b.build(__is_aws_mode(context))
        Context(context).add_app(app)


def __is_aws_mode(context):
    try:
        return context.config.userdata['mode'] == 'aws'
    except KeyError:
        return False


def __push_apps_aws(apps):
    for app in apps:
        AWSImagePusher(app).push()


def after_scenario(context, scenario):
    for ns in Context(context).pop_namespaces_to_delete():
        K8sDriver(ns).delete_namespace()


def before_scenario(context, scenario):
    __create_namespace(context)
    RecipeRepository().create()
    ConfigRepository().create()


def __create_namespace(context):
    namespace = getpass.getuser() + "-" + str(int(time.time()))
    print ("namespace:%s" % (namespace))
    k8s = K8sDriver(namespace, context.minikube)
    k8s.create_namespace()
    Context(context).set_default_namespace(namespace)
    k8s.upload_config('default')

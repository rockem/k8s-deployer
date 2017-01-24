from deployer.log import DeployerLogger
from features.steps.configurer_steps import delete_namespace
from features.steps.support import push_to_git
from steps.support import create_namespace, delete_java_service_from_k8s, delete_java_image_from_registry, create_repo,\
    update_k8s_configuration, upload_java_image_to_registry

logger = DeployerLogger(__name__).getLogger()


def before_all(context):
    create_namespace(context)
    upload_java_image_to_registry()


def before_feature(context, feature):
    update_k8s_configuration()


def after_all(context):
    delete_namespace(context)
    delete_java_image_from_registry()


def before_scenario(context, scenario):
    create_repo()
    push_to_git()
    delete_java_service_from_k8s()



def after_scenario(context, scenario):
    if 'service is created in a namespace' == scenario.name:
        delete_namespace(context, 'non-existing-namespace')
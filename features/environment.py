from features.steps.deployer_steps import delete_namespace
from steps.support import create_namespace, delete_java_service_from_k8s, delete_java_image_from_registry, create_repo,\
    update_k8s_configuration, upload_java_image_to_registry
from deployer.log import DeployerLogger

logger = DeployerLogger(__name__).getLogger()


def before_all(context):
    create_namespace()
    upload_java_image_to_registry()


def before_feature(context, feature):
    update_k8s_configuration()


def after_all(context):
    delete_namespace(context)
    delete_java_image_from_registry()


def before_scenario(context, scenario):
    create_repo()
    delete_java_service_from_k8s()


#todo use case for 2 scenario one with file , and one without
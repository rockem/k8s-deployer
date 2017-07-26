from features.support.docker import AppImage

LAST_DEPLOYED = 'lastDeployed'
APPS = 'apps'
NS_TO_DELETE = 'ns-delete'


class Context:
    def __init__(self, context):
        self.context = context

    def add_app(self, app):
        try:
            self.__user_data()[APPS]
        except KeyError:
            self.__user_data()[APPS] = {}
        self.__user_data()[APPS][app.app_key()] = app

    def __user_data(self):
        return self.context.config.userdata

    def get_app_for(self, name, version):
        app_key = AppImage.app_key_for(name, version)
        app = self.__user_data()[APPS][app_key]
        return app

    def all_apps(self):
        return self.__user_data()[APPS].values()

    def set_last_deployed_app(self, app):
        self.__user_data()[LAST_DEPLOYED] = app

    def last_deployed_app(self):
        return self.__user_data()[LAST_DEPLOYED]

    def add_namespace_to_delete(self, namespace):
        try:
            self.__user_data()[NS_TO_DELETE]
        except:
            self.__user_data()[NS_TO_DELETE] = []
        self.__user_data()[NS_TO_DELETE].append(namespace)

    def namespaces_to_delete(self):
        return  self.__user_data()[NS_TO_DELETE]

    def set_default_namespace(self, namespace):
        self.__user_data()["namespace"] = namespace
        self.add_namespace_to_delete(namespace)

    def default_namespace(self):
        return self.__user_data()["namespace"]


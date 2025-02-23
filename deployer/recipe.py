import copy

from log import DeployerLogger

EXPOSE_LABEL = 'expose'
IMAGE_LABEL = 'image_name'
LOGGING_LABEL = 'logging'
PORTS_LABEL = 'ports'
SERVICE_TYPE = 'service_type'
METRICS_LABEL = 'metrics'
ADMIN_PRIVILEGES_LABEL = 'adminPrivileges'
AUTOSCALE_LABEL = 'autoscale'
INGRESS_LABEL = 'ingress'

logger = DeployerLogger(__name__).getLogger()


class RecipeError(Exception):
    def __init(self, message):
        super(RecipeError, self).__init__(message)


class RecipeBuilder(object):
    _ingredients = {}
    _image = None

    def ingredients(self, ingredients):
        self._ingredients = ingredients
        return copy.copy(self)

    def image(self, image):
        self._image = image
        return copy.copy(self)

    def build(self):
        if self._image is not None:
            self._ingredients[IMAGE_LABEL] = self._image
        return Recipe(self._ingredients)


class Recipe(object):
    LOGGING_DEFAULT = 'log4j'
    EXPOSE_DEFAULT = True
    SERVICE_TYPE_UI = 'ui'
    SERVICE_TYPE_API = 'api'
    SERVICE_TYPE_INTERNAL_UI = 'internal_ui'

    def __init__(self, ingredients):
        self.ingredients = ingredients
        self.__set_defaults()

    def __set_defaults(self):
        if not self.ingredients.has_key(LOGGING_LABEL):
            self.ingredients[LOGGING_LABEL] = self.LOGGING_DEFAULT
        if not self.ingredients.has_key(EXPOSE_LABEL):
            self.ingredients[EXPOSE_LABEL] = self.EXPOSE_DEFAULT
        if not self.ingredients.has_key(SERVICE_TYPE):
            self.ingredients[SERVICE_TYPE] = self.SERVICE_TYPE_API
        if PORTS_LABEL not in self.ingredients:
            self.ingredients[PORTS_LABEL] = []
        if METRICS_LABEL not in self.ingredients:
            self.ingredients[METRICS_LABEL] = {'enabled': False}
        if ADMIN_PRIVILEGES_LABEL not in self.ingredients:
            self.ingredients[ADMIN_PRIVILEGES_LABEL] = {'enabled': False}
        if AUTOSCALE_LABEL not in self.ingredients:
            self.ingredients[AUTOSCALE_LABEL] = {'enabled': False}
        if INGRESS_LABEL not in self.ingredients:
            self.ingredients[INGRESS_LABEL] = {'enabled': False}

    @staticmethod
    def builder():
        return RecipeBuilder()

    def image(self):
        return self.ingredients[IMAGE_LABEL]

    def logging(self):
        return self.ingredients[LOGGING_LABEL]

    def expose(self):
        expose = self.ingredients[EXPOSE_LABEL]
        if not isinstance(expose, bool):
            raise RecipeError('%s is not a valid value' % expose)
        return expose

    def service_type(self):
        return self.ingredients[SERVICE_TYPE]

    def ports(self):
        return self.ingredients[PORTS_LABEL]

    def metrics(self):
        return self.ingredients[METRICS_LABEL]

    def admin_privileges(self):
        return self.ingredients[ADMIN_PRIVILEGES_LABEL]

    def autoscale(self):
        return self.ingredients[AUTOSCALE_LABEL]

    def ingress(self):
        return self.ingredients[INGRESS_LABEL]

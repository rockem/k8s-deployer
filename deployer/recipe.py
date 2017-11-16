import copy

from log import DeployerLogger

EXPOSE_LABEL = 'expose'
IMAGE_LABEL = 'image_name'
LOGGING_LABEL = 'logging'
PORTS_LABEL = 'ports'
SERVICE_TYPE = 'service_type'

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
    SERVICE_TYPE_DEFAULT = SERVICE_TYPE_UI

    def __init__(self, ingredients):
        self.ingredients = ingredients
        self.__set_defaults()

    def __set_defaults(self):
        if not self.ingredients.has_key(LOGGING_LABEL):
            self.ingredients[LOGGING_LABEL] = self.LOGGING_DEFAULT
        if not self.ingredients.has_key(EXPOSE_LABEL):
            self.ingredients[EXPOSE_LABEL] = self.EXPOSE_DEFAULT
        if not self.ingredients.has_key(SERVICE_TYPE):
            self.ingredients[SERVICE_TYPE] = self.SERVICE_TYPE_DEFAULT
        if PORTS_LABEL not in self.ingredients:
            self.ingredients[PORTS_LABEL] = []

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

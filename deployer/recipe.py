import copy

from log import DeployerLogger

EXPOSE_LABEL = 'expose'
IMAGE_LABEL = 'image_name'

logger = DeployerLogger(__name__).getLogger()

class RecipeError(Exception):
    def __init(self, message):
        super(RecipeError, self).__init__(message)

class RecipeBuilder(object):
    _ingredients = None
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
    def __init__(self, ingredients):
        self.ingredients = ingredients

    @staticmethod
    def builder():
        return RecipeBuilder()

    def image(self):
        return self.ingredients[IMAGE_LABEL]

    def expose(self):
        try:
            expose = self.ingredients[EXPOSE_LABEL]
        except KeyError:
            return True

        if not isinstance(expose, bool):
            raise RecipeError('%s is not a valid value' %expose)

        return expose
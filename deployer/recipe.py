import copy

import yaml

from log import DeployerLogger

EXPOSE_LABEL = 'expose'
IMAGE_LABEL = 'image_name'

logger = DeployerLogger(__name__).getLogger()

class RecipeBuilder(object):
    path = None

    def indgredients(self, path):
        self.path = path
        return self

    def image(self, image):
        self.image = image
        return copy.copy(self)

    def build(self):
        ingredients = {IMAGE_LABEL : self.image}
        try:
            content = self.__open_file_for(self.path)
            ingredients.update(yaml.load(content))
        except IOError:
            pass
        return Recipe(ingredients)


    def __open_file_for(self, path):
        f = open(str(path), "r+")
        return f


class Recipe(object):
    def __init__(self, indgredients):
        self.indgredients = indgredients

    @staticmethod
    def builder():
        return RecipeBuilder()

    def image(self):
        return self.indgredients[IMAGE_LABEL]

    def expose(self):
        try:
            expose = self.indgredients[EXPOSE_LABEL]
        except KeyError:
            return True

        if not isinstance(expose, bool):
            raise ValueError

        return expose
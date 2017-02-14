import yaml


class RecipeExtractor(object):

    def extract(self, value):
        value = str(value).lower()
        if value == 'false':
            return False
        elif value == 'true':
            return True
        else:
            raise ValueError('not proper value')


class Recipe(object):
    def __init__(self, path):
        self.path = path
        self.extractor = RecipeExtractor()
        self.recipe = None

    def expose(self):
        try:
            content = self.__open_file_for(self.path)
            self.recipe = yaml.load(content)
        except IOError as e:
            return True

        return self.extractor.extract(self.recipe.get('expose'))

    def __open_file_for(self, path):
        f = open(str(path), "r+")
        return f

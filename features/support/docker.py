import json
import os

import subprocess


class AppImage:
    AWS_REGISTRY_URI = "911479539546.dkr.ecr.us-east-1.amazonaws.com"

    def __init__(self, name, version, aws_mode):
        self._name = name
        self._version = version
        self._aws_mode = aws_mode
        self._service_name = 'deployer-test-%s' % self._name

    def service_name(self):
        return self._service_name

    def name(self):
        return self._name

    def sevice_name(self):
        return self._service_name

    def version(self):
        return self._version

    def image_name(self):
        if self._aws_mode:
            return '%s/%s' % (self.AWS_REGISTRY_URI, self.__service_name_version())
        return '%s' % self.__service_name_version()

    def __service_name_version(self):
        return "%s:%s" % (self._service_name, self._version)

    def app_key(self):
        return self.app_key_for(self._name, self._version)

    @staticmethod
    def app_key_for(name, version):
        return "%s:%s" % (name, version)

    def recipe_path(self):
        return "./features/apps/%s/recipe.yml" % self._name


class AppImageBuilder:
    def __init__(self, name, version, *args):
        self.name = name
        self.version = version
        self.args = args

    def build(self, aws_mode):
        app_image = AppImage(self.name, self.version, aws_mode)
        print 'Building %s' % app_image.image_name()
        self.run_command(self.__create_build_command(app_image, aws_mode))
        return app_image

    def run_command(self, command):
        os.system('cd features/apps/%s; %s' % (self.name, ' '.join(command)))

    def __create_build_command(self, app_image, aws_mode):
        command = []
        if not aws_mode:
            command += ['eval $(minikube docker-env);']
        command += ['docker', 'build']
        try:
            for b in self.args:
                command += ['--build-arg', b[0]]
        except KeyError:
            pass
        return command + ['-t', app_image.image_name(), '.']


class JavaAppBuilder:
    def __init__(self, app_builder):
        self.app_builder = app_builder

    def build(self, *build_args):
        self.app_builder.run_command(['./gradlew', 'clean', 'build'])
        return self.app_builder.build(*build_args)

    def image_name(self):
        return self.app_builder.image_name()


class AWSImagePusher:
    def __init__(self, app):
        self.app = app

    def push(self):
        if not self.__is_image_exists_in_aws(self.app.sevice_name(), self.app.version()):
            subprocess.check_output('docker push %s' % (self.app.image_name()),
                                    shell=True)

    def __is_image_exists_in_aws(self, name,version):

        try:
            output = subprocess.check_output(
                'aws ecr batch-get-image --repository-name %s --image-ids imageTag=%s' % (name, version),
                shell=True)
            return len(json.loads(output)['images']) > 0
        except:
            return False



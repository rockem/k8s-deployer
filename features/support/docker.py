import json
import os

import subprocess


class AppImage:
    AWS_REGISTRY_URI = "911479539546.dkr.ecr.us-east-1.amazonaws.com"

    def __init__(self, name, version):
        self.name = name
        self.version = version

    def image_name(self, aws_mode):
        app_name = self.__app_name()
        return '%s' % app_name if aws_mode else '%s/%s' % (self.AWS_REGISTRY_URI, app_name)

    def __app_name(self):
        return 'deployer-test-%s:%s' % (self.name, self.version)


class AppImageBuilder:
    def __init__(self, app_image, *args):
        self.app_image = app_image
        self.args = args

    def build(self, aws_mode):
        print 'Building %s' % self.app_image.image_name(aws_mode)
        self.run_command(self.__create_build_command(aws_mode))

    def run_command(self, command):
        os.system('cd features/apps/%s; %s' % (self.app_image.name, ' '.join(command)))

    def image_name(self):
        return self.app_image.image_name()

    def __create_build_command(self, aws_mode):
        command = []
        if not aws_mode:
            command += ['eval $(minikube docker-env);']
        command += ['docker', 'build']
        try:
            for b in self.args:
                command += ['--build-arg', b[0]]
        except KeyError:
            pass
        return command + ['-t', self.app_image.image_name(aws_mode), '.']


class JavaAppBuilder:
    def __init__(self, app_builder):
        self.app_builder = app_builder

    def build(self, *build_args):
        self.app_builder.run_command(['./gradlew', 'clean', 'build'])
        self.app_builder.build(*build_args)

    def image_name(self):
        return self.app_builder.image_name()


class AWSImagePusher:

    def __init__(self, builder):
        self.builder = builder

    def push(self, aws_mode):
        self.builder.build(aws_mode)
        if aws_mode:
            self.__push_to_aws()

    def __push_to_aws(self):
        # self.__tag_for_aws(self.builder.image_name())
        if not self.__is_image_exists_in_aws(self.builder.image_name()):
            subprocess.check_output('docker push %s' % (self.builder.image_name()),
                                    shell=True)

    def __tag_for_aws(self, image_name):
        subprocess.call('docker tag %s %s' %
                        (image_name, self.__get_aws_image_for(image_name)), shell=True)

    def __is_image_exists_in_aws(self, image_name):
        name = image_name.split(':')[0]
        version = image_name.split(':')[1]
        output = subprocess.check_output(
            'aws ecr batch-get-image --repository-name %s --image-ids imageTag=%s' % (name, version),
            shell=True)

        return len(json.loads(output)['images']) > 0

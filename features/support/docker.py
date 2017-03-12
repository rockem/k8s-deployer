import os


class AppImageBuilder:

    def __init__(self, spec):
        self.spec = spec

    def build(self, aws_mode):
        print 'Building %s' % self.__image_name()
        self.run_command(self.__create_build_command(aws_mode))

    def run_command(self, command):
        os.system('cd features/apps/%s; %s' % (self.spec['name'], ' '.join(command)))

    def __image_name(self):
        return 'deployer-test-%s:%s' % (self.spec['name'], self.spec['version'])

    def __create_build_command(self, aws_mode):
        command = []
        if not aws_mode:
            command += ['eval $(minikube docker-env);']
        command += ['docker', 'build']
        try:
            for b in self.spec['args']:
                command += ['--build-arg', b[0]]
        except KeyError:
            pass
        return command + ['-t', self.__image_name(), '.']


class JavaAppBuilder:

    def __init__(self, app_pusher):
        self.app_pusher = app_pusher

    def build(self, *build_args):
        self.app_pusher.run_command(['./gradlew', 'clean', 'build'])
        self.app_pusher.build(*build_args)



import os
import subprocess


class AppPusher:

    def __init__(self, app, version):
        self.app = app
        self.version = version

    def push(self, *build_args):
        print 'Building %s' % self.__image_name()
        self.run_command(self.__create_build_command(build_args))
        # print 'Pushing %s' % self.__image_name()
        # self.run_command(['docker', 'push', self.__image_name()])

    def run_command(self, command):
        # subprocess.call(
        #     command,
        #     cwd=('features/apps/%s' % self.app))
        os.system('cd features/apps/%s; eval $(minikube docker-env); %s' % (self.app, ' '.join(command)))

    def __image_name(self):
        return 'deployer-test-%s:%s' % (self.app, self.version)

    def __create_build_command(self, *build_args):
        command = ['docker', 'build']
        if all(build_args):
            for b in build_args:
                command += ['--build-arg', b[0]]
        return command + ['-t', self.__image_name(), '.']


class JavaAppPusher:

    def __init__(self, app_pusher):
        self.app_pusher = app_pusher

    def push(self, *build_args):
        self.app_pusher.run_command(['./gradlew', 'clean', 'build'])
        self.app_pusher.push(*build_args)



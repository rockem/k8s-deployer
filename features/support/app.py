import re
import time

import subprocess


class AppDriver:

    def __init__(self, app):
        self.app = app

    def is_running(self):
        pass

    def __busy_wait(run_func, *args):
        result = False
        for _ in range(20):  # TODO - should be 120
            try:
                if run_func(*args):
                    result = True
                    break
            except Exception:
                pass
            time.sleep(1)

        return result


    def __pod_running(self, image_name):
        pod_name = self.__grab_pod_name(image_name)
        match = re.search(r"Status:\s(.*)", self.__describe_pod(pod_name))
        if match:
            return match.group(1).strip() == 'Running'
        else:
            raise Exception('service %s has no pod!' % pod_name)


    def __describe_pod(self, pod_name):
        return self, __run("kubectl --namespace %s describe pods %s" % (NAMESPACE, pod_name))


    def __grab_pod_name(self, pod_name):
        output = self, __run("kubectl --namespace %s get pods" % (NAMESPACE))
        list = output.split()
        for item in list:
            if item.startswith(pod_name):
                return item

    def __run(self, command):
        return subprocess.check_output(command, shell=True)

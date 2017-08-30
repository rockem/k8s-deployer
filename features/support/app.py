import time


class AppDriver:
    NUM_ITER = 160
    def __init__(self, app):
        self.app = app

    def is_running(self):
        pass

    @staticmethod
    def busy_wait(run_func, *args):
        for i in range(AppDriver.NUM_ITER):
            try:
                return run_func(*args)
            except Exception :
                 pass
            time.sleep(1)
        raise Exception

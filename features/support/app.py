import time


class AppDriver:
    NUM_ITER = 120
    def __init__(self, app):
        self.app = app

    def is_running(self):
        pass

    @staticmethod
    def busy_wait_bool(run_func, *args):
        result = False
        for i in range(AppDriver.NUM_ITER):
            try:
                if run_func(*args):
                    result = True
                    break
            except Exception:
                pass
            time.sleep(1)
        return result

    @staticmethod
    def busy_wait(run_func, *args):
        for i in range(AppDriver.NUM_ITER):
            try:
                run_func(*args)
                return
            except Exception:
                if (AppDriver.__isLastIter(i , AppDriver.NUM_ITER)):
                    run_func(*args)
                else:
                    pass
            time.sleep(1)

    @staticmethod
    def __isLastIter(index,size):
        return index == size - 1
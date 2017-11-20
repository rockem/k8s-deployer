import time


class TimeoutError(Exception):
    pass


class BusyWait(object):

    def __init__(self, retries=60):
        self.retries = retries

    def execute(self, run_func, *args):
        curr_e = None
        for i in range(self.retries):
            try:
                return run_func(*args)
            except Exception as e:
                curr_e = e
            time.sleep(1)
        raise curr_e

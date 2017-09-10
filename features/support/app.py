import time


class BusyWait:
    NUM_ITER = 160

    @staticmethod
    def execute(run_func, *args):
        for i in range(BusyWait.NUM_ITER):
            try:
                return run_func(*args)
            except Exception :
                 pass
            time.sleep(1)
        raise Exception

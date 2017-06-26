import time


class AppDriver:

    def __init__(self, app):
        self.app = app

    def is_running(self):
        pass

    @staticmethod
    def busy_wait(run_func, *args):
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
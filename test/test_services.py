import yaml

from deployer.services import ConfigUploader


class ConnectorStub:
    expected_job = []

    def __init__(self):
        pass

    def upload_job(self, job):
        self.expected_job.append(job)

    def init(self):
        del self.expected_job[:]




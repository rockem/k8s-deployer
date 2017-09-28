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


class TestConfigUploader:

    JOB1 = {'name': 'job1', 'schedule': '*/1 * * * *', 'url': 'job1/run'}
    JOB2 = {'name': 'job2', 'schedule': '*/1 * * * *', 'url': 'job2/run'}
    connector = ConnectorStub()

    def __init__(self):
        pass

    def setup(self):
        self.connector.init()

    def test_upload_job_successfully(self):
        config_uploader = ConfigUploader(self.connector)
        input_jobs_yml = './input_jobs.yml'
        self.__generate_jobs_file(input_jobs_yml, [self.JOB1, self.JOB2])
        config_uploader.upload_jobs(input_jobs_yml)

        self.__jobs_are_the_same(self.connector.expected_job, [self.JOB1, self.JOB2])

    def __jobs_are_the_same(self, jobs_list, expected_jobs_list):
        assert len(jobs_list) == len(expected_jobs_list)
        for job in jobs_list:
            assert job in expected_jobs_list

    def __generate_jobs_file(self, path, jobs_list):
        jobs_structure = self.__create_jobs_structure_from(jobs_list)
        with open(path, 'w') as outfile:
            yaml.dump(jobs_structure, outfile, default_flow_style=False)

    def __create_jobs_structure_from(self, jobs_list):
        jobs_structure = dict(jobs=[])
        for job in jobs_list:
            jobs_structure['jobs'].append(
                {job['name']: dict(schedule=job['schedule'], url=job['url'])}
            )
        return jobs_structure

    def test_dont_upload_jobs_on_missing_file(self):
        config_uploader = ConfigUploader(self.connector)
        config_uploader.upload_jobs(None)
        assert len(self.connector.expected_job) == 0

    def test_dont_upload_jobs_on_empty_file(self):
        config_uploader = ConfigUploader(self.connector)
        empty_jobs_yml = './input_jobs.yml'
        self.__generate_jobs_file(empty_jobs_yml, [])
        config_uploader.upload_jobs(empty_jobs_yml)

        assert len(self.connector.expected_job) == 0

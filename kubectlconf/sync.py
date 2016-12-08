import subprocess
import os
import shutil
import datetime


class S3ConfSync:

    CONFIG_FILE_DIRECTORY = os.path.expanduser('~') + '/.kube'
    CONFIG_FILE = CONFIG_FILE_DIRECTORY + '/config'
    TEMP_DIRECTORY = "/tmp/agt/k8s"
    TEMP_CONFIG_FILE_DIRECTORY = TEMP_DIRECTORY + '/k8s-structs/config'
    TEMP_CONFIG_FILE = TEMP_DIRECTORY + '/k8s-structs/config/config'

    def __init__(self, setup_name):
        self.setup_name = setup_name

    def sync(self):
        print 'syncing s3://agt-terraform-state-prod/' + self.setup_name
        self.create_temp_directory()
        self.sync_with_s3(self.setup_name)
        self.backup_old_configuration()
        self.use_new_config()

    def create_temp_directory(self):
        shutil.rmtree(self.TEMP_DIRECTORY, True)
        os.makedirs(self.TEMP_DIRECTORY)

    def sync_with_s3(self, setup_name):
        subprocess.call('aws s3 sync s3://agt-terraform-state-prod/'
                         + setup_name + '/cfssl ' + self.TEMP_DIRECTORY + '/.cfssl', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        subprocess.call('aws s3 sync s3://agt-terraform-state-prod/'
                        + setup_name + '/k8s-structs ' + self.TEMP_CONFIG_FILE_DIRECTORY, shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def backup_old_configuration(self):
        today = datetime.datetime.today()
        if os.path.exists(self.CONFIG_FILE):
            shutil.copy(self.CONFIG_FILE, self.CONFIG_FILE + '_' + today.strftime('%Y%m%d_%H:%M:%S'))
            os.remove(self.CONFIG_FILE)

    def use_new_config(self):
        if os.path.exists(self.TEMP_CONFIG_FILE):
            self.copy_config(self.TEMP_CONFIG_FILE)

    def copy_config(self, new_config):
        if not os.path.exists(self.CONFIG_FILE_DIRECTORY):
            os.makedirs(self.CONFIG_FILE_DIRECTORY)
        if os.path.isfile(self.TEMP_CONFIG_FILE):
            shutil.copy(new_config, self.CONFIG_FILE)

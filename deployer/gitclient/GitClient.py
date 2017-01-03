import os
import shutil
import git


class GitClient(object):

    def get_repo(self, url, to_path):
        print 'get url:%s ,repo:%s' % (url, to_path)
        return git.Repo.clone_from(url, to_path)

    def push(self, file_name, repo, service_name, image_name):
        repo.index.add([file_name])
        repo.index.commit("Updating service %s with version %s" % (service_name, image_name))
        repo.rem

    def delete_checkout_dir(self, checkout_dir):
        if os.path.isdir(checkout_dir):
            shutil.rmtree(checkout_dir)

    def create_directory(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)

    def init(self, path):
        print 'init repo %s' % path
        git.Repo.init(path=path)

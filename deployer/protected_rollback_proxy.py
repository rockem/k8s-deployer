import time


class ProtectedRollbackProxy:
    def __init__(self, repository, env, service_name=None):
        self.repository = repository
        self.env = env
        self.service_name = service_name

    def write_deployment(self, recipe_data):
        self.repository.write_deployment({"service_name": self.service_name, "env": self.env, "rolled_back": False,
                                         "timestamp": int(round(time.time() * 1000)), "recipe": recipe_data})

    def get_previous_recipe(self):

        current_deployment = self.repository.get_current_deployment(self.service_name, self.env)

        self.check_if_newer_deployment_exist(
            self.repository.get_all_deployment_from_time(self.env, current_deployment['timestamp'], self.service_name))

        return self.repository.get_previous_deployment(self.service_name, self.env)['recipe']

    def check_if_newer_deployment_exist(self, deployments_lst):
        if len(deployments_lst) > 0:
            self.raise_not_latest_deployment_error(deployments_lst)

    def raise_not_latest_deployment_error(self, filtered_lst):
        msg = ""
        for deployment in filtered_lst:
            msg += deployment['service_name'] + ', '
        raise NotLatestDeployment('there are newer services that were deployed after {0} : {1}'
                                  .format(self.service_name, msg))

    def get_all_recipes(self):
        return self.repository.get_all_recipes(self.env)

    def rollback(self):
        self.repository.rollback(self.service_name, self.env)



class NotLatestDeployment(Exception):
    def __init(self, message):
        super(NotLatestDeployment, self).__init__(message)
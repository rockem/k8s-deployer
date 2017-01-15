Feature: K8s global configuration

  Scenario: A service in k8s is using the k8s global configuration
#    Given k8s has global configuration
    #deploying
    When deploying to namespace
    Then the service should get the new configuration
    # service configuration is overridden by global
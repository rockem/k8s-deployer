Feature: K8s global configuration

  Scenario: A service in k8s is using the k8s global configuration
    When deploying to namespace
    Then the service should get the new configuration

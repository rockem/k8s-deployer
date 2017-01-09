Feature: Apply configuration to a service using k8s config map

  Scenario: A service in k8s is using the k8s global configuration
    Given k8s has global configuration
    When a new java service is deployed to k8s
    Then the service should get the new configuration
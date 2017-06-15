Feature: promote service on k8s

  Scenario: service is promoted according to git content of source environment
    Given "healthy:1.0" service is defined in int environment
    When promoting
    Then it should be running
    #And service should be logged in "prod"
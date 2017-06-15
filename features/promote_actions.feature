Feature: promote service on k8s

  Scenario: service is promoted according to git content of source environment
    Given "healthy:1.0" logged for "int"
    When promoting
    Then "healthy:1.0" is deployed
    And service should be logged in "prod"
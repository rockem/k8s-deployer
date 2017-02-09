Feature: promote service on k8s

  Scenario: service is promoted according to git content of source environment
    Given service is defined in source environment
    When promoting to production
    Then service is deployed
    And service should be logged in git
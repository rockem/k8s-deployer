Feature: promote service on k8s

  Scenario: service is promoted according to git content of source environment
    Given "version:healthy" service is defined in int environment
    When promoting
    Then it should be running
    And it should be logged in git
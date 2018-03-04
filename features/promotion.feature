Feature: promote service on k8s

  Scenario: service is promoted according to git content of source environment
    Given "version:healthy" service is defined in kuku environment
    And swagger is defined in kuku environment
    When promoting from kuku environment to int
    Then it should be running
    And it should be logged in mongo

  Scenario: swagger is promoted according to git content of source environment
    Given "version:healthy" service is defined in kuku environment
    And swagger is defined in kuku environment
    When promoting from kuku environment to int
    Then uploaded to api gw
    And swagger logged in git
    
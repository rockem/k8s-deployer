Feature: deploy service on k8s

  Scenario: deploy simple service
    Given service is dockerized
    When deploying
    Then service should be deployed

  Scenario: service is written to git after deployment
    Given service is dockerized
    When deploying
    Then service should be logged in git

  Scenario: service is promoted according to git content of source environment
    Given service is defined in source environment
    When promoting to production
    Then service should be deployed in production
    And service should be logged in git
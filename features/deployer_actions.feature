Feature: deploy service on k8s

  Scenario: deploy simple service
    When deploying to namespace
    Then service should be deployed

  Scenario: service is written to git after deployment
    When deploying to namespace
    Then service should be logged in git

  Scenario: service is promoted according to git content of source environment
    Given service is defined in source environment
    When promoting to production
    Then service should be deployed
    And service should be logged in git

  Scenario: service is created in a namespace
    Given namespace "non-existing-namespace" doesn't exists
    When deploying to namespace "non-existing-namespace"
    Then service should be deployed in "non-existing-namespace"
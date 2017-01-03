Feature: deploy service on k8s

  Scenario: deploy simple service
    Given service is dockerized
    When execute
    Then service should be deployed

  Scenario: service is written to git after deployment
    Given service is dockerized
    When execute
    Then service name and version is written to git

  Scenario: service is promoted from integration to production
    Given service is in integration
    When promoting to production
    Then service should be deployed in production
    And the promoted service should be logged in git
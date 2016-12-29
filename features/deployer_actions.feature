Feature: deploy service on k8s

  Scenario: deploy simple service
    Given service is dockerized
    When execute
    Then service should be deployed

  Scenario: service is written to git after deployment
    Given service is dockerized
    When execute
    Then service name and version is written to git
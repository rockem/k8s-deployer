Feature: deploy service on k8s

  Scenario: deploy simple service
    Given service is dockerized
    When execute
    Then service should be deployed
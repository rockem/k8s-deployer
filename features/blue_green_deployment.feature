Feature: dark deploy service to k8s

  Scenario: healthy service still serving when sick service deployed
    Given login
    When deploy healthy service
    And deploy sick service should fail
    Then healthy service still serving
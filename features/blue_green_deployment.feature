Feature: dark deploy service to k8s

  Scenario: healthy service still serving when sick service deployed
    When deploy healthy service
    And deploy sick service should fail
    Then healthy service still serving

  Scenario: updated service
    When deploy hello:1 service
    And deploy hello:2 service
    Then service updated to version 2

  Scenario: skip health check if service marked as "ignored"
    When deploy ignored_health service
    Then service health is deployed
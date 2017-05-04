Feature: dark deploy service to k8s

  Scenario: healthy service still serving when sick service deployed
    When deploy "healthy:1.0" service
    And deploy "sick:1.0" service should fail
    Then "healthy:1.0" service is serving

  Scenario: updated service
    When deploy "version:1.0" service
    And deploy "version:2.0" service
    Then service "version" updated to version 2.0
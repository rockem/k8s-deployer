Feature: Update k8s configuration

  Scenario: Upload configMap from git to specific namespace
    Given config "kuku" was pushed to git
    When configuring
    Then config "kuku" uploaded

  Scenario: Creating namespace if it not exists
    Given config "kuku" was pushed to git
    And namespace "non-existing-namespace" doesn't exists
    When configuring "non-existing-namespace"
    Then config "kuku" uploaded to "non-existing-namespace" namespace

  Scenario: Upload job from git to specific namespace
    Given "stateful:1.0" service was deployed successfully
    And job "jobs" was pushed to git
    When configuring
    Then the job for "stateful:1.0" service was invoked

  Scenario: deploy swagger to apigateway
    Given swagger is defined in int environment
    When deploying swagger
    Then uploaded to api gw
    And swagger logged in git
    
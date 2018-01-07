Feature: Update k8s configuration

  Scenario: upload configMap folders to specific namespace
    Given folder "kuku-configs" was pushed to git
    When configuring
    Then folder "kuku-configs" uploaded


  Scenario: Creating namespace if it not exists
    Given config "kuku.yml" was pushed to git
    And namespace "non-existing-namespace" doesn't exists
    When configuring "non-existing-namespace"
    Then config "kuku.yml" uploaded to "non-existing-namespace" namespace

  @eli
  Scenario: Upload job from git to specific namespace
    Given "stateful:2.0" service was deployed successfully
    And job "jobs.yml" was pushed to git
    When configuring
    Then the job for "stateful:2.0" service was invoked

  Scenario: deploy swagger to apigateway
    Given swagger is defined in int environment
    When deploying swagger
    Then uploaded to api gw
    And swagger logged in git


    
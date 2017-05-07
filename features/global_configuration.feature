@pushed_global_config
Feature: Update k8s configuration

  Scenario: Upload configMap from git to specific namespace
    Given config "kuku" was pushed to git
    When configuring
    Then config "kuku" uploaded

  @without_default_namespace
  Scenario: Creating namespace if it doesn't exists
    Given config "kuku" was pushed to git
    And namespace "non-existing-namespace" doesn't exists
    When configuring "non-existing-namespace"
    Then config "kuku" uploaded to "non-existing-namespace" namespace


@pushed_global_config
Feature: Update k8s configuration

  Scenario: Upload configMap from git to specific namespace
    When configuring
    Then config uploaded

  Scenario: creating namespace if not exists
    Given namespace "non-existing-namespace" doesn't exists
    When configuring "non-existing-namespace"
    Then config uploaded to "non-existing-namespace" namespace
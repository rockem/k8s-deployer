#@pushed_global_config
Feature: Update k8s configuration

  Scenario: Upload configMap from git to specific namespace
    Given config "kuku" was pushed to git
    When configuring
    Then config "kuku" uploaded

  Scenario: Creating namespace if it not exists
    Given config "kuku" was pushed to git
    And namespace "inna-amazia" doesn't exists
    When configuring "inna-amazia"
    Then config "kuku" uploaded to "inna-amazia" namespace


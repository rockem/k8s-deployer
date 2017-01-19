Feature: Update k8s configuration

  Scenario: Upload configMap from git to specific namespace
    Given config file exists in git
    When configuring
    Then config uploaded to k8s
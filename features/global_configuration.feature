Feature: Update k8s configuration

  Scenario: Upload configMap from git to specific namespace
    Given config "kuku" was pushed to git
    When configuring
    Then config "kuku" uploaded

  @create_custom_namespace:non-existing-namespace
  Scenario: Creating namespace if it not exists
    Given config "kuku" was pushed to git
    And namespace "non-existing-namespace" doesn't exists
    When configuring "non-existing-namespace"
    Then config "kuku" uploaded to "non-existing-namespace" namespace


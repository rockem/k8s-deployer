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


    
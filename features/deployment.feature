Feature: deploy service on k8s

  Scenario: deploy simple service
    When deploy "version:healthy" service
    Then "version:healthy" service is serving

  Scenario: service is written to git after deployment
    When deploy "version:healthy" service
    Then it should be logged in git

  Scenario: deploy restless service
    When deploy "restless:1.0" service
    Then it should be running

  Scenario: recipe written to git after deployment
    When deploy "restless:1.0" service
    Then recipe should be logged in git

  Scenario: expose another port
    When deploy "ported:1.0" service
    Then port 5000 is available



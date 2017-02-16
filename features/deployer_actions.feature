Feature: deploy service on k8s

  Scenario: deploy simple service
    When deploying to namespace
    Then service is deployed

  Scenario: service is written to git after deployment
    When deploying to namespace
    Then service should be logged in git

  Scenario: deploy restless service
    When deploy "restless" service
    Then pod is up and running

  Scenario: recipe written to git after deploy
    When deploy "restless" service
    Then expose property should be logged in git
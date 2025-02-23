Feature: deploy service on k8s

  Scenario: deploy simple service
    When deploy "version:healthy" service
    Then "version:healthy" service is serving

  Scenario: healthy service with autoscale enabled will deploy with able to scale
    When deploy "autoscaled:1.1" service
    Then "autoscaled:1.1" service is serving
    And it should have deployment with autoscaler

  Scenario: healthy service with ingress will expose ingress
    When deploy "ingress:1.0" service
    Then "ingress:1.0" service is serving
    And  it should have ingress

  Scenario: service is written to git after deployment
    When deploy "version:healthy" service
    Then it should be logged in mongo

  Scenario: deploy restless service
    When deploy "restless:1.0" service
    Then it should be running

  Scenario: recipe written to git after deployment
    When deploy "restless:1.0" service
    Then recipe should be logged in mongo

  Scenario: expose another port
    When deploy "ported:1.0" service
    Then port 5000 is available

  Scenario: force deploy service
    When force deploy "version:sick" service should succeed
    Then all is good



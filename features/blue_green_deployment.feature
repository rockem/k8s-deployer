#Feature: dark deploy service to k8s
#
#  Scenario: healthy service still serving when sick service deployed
#    When deploy "version:healthy" service
#    And deploy "version:sick" service should fail
#    Then "version:healthy" service is serving

#  Scenario: updated service
#    When deploy "version:1.0" service
#    And deploy "version:2.0" service
#    Then service "version" updated to version 2.0

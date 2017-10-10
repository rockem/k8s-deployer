#Feature: Consume configuration
#
#  Scenario: Java service global config override local config
#    Given config "greeter" was uploaded
#    When deploy "java:1.0" service
#    Then the service should get the new configuration
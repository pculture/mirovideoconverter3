Feature: Clear Finished Conversions

    Scenario:  Clear a finished conversion
        Given I have converted a file
        When I clear finished conversions
        Then the completed file is removed from the list

    Scenario: Clear finished conversions while others are in progress
        Given I have a finished conversion
            And I have some conversions in progress
        When I clear finished conversions
        Then the completed files are removed
            And the in-progress conversions remain.
   
    Scenario: Clear finished conversions after conversion errors
        Given I have a finished conversion
            And I have a failed conversion
        When I clear finished conversions
        Then the completed files are removed
            And the failed conversions are removed

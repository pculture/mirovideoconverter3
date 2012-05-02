Feature: Choose the conversion settings
    As a user
    I want to choose the output format and size settings
    

    Scenario Outline:  Choose a device type
        Given I have files in the list of files
        When I choose a "<device>"
        Then it is selected
    Examples: 
        | device |
        | iPad |
        | Xoom |
        | PSP |

    Scenario Outline:  Choose custom format
        Given I have files in the list of files
        When I choose a "<custom>" output format
        Then it is selected
    Examples:
        | custom |
        | FLV  |
        | MP4 |
        | MP3 |

        
    Scenario: Choose custom size
        Given I have files in the list of files
        When I choose an output size
        Then it is selected

    Scenario: Choose custom aspect ratio
        Given I have files in the list of files
        When I choose the aspect ratio
        Then it is selected

    Scenario: Choose qtfaststart 
        Given I have files in the list of files
        When I choose the qtfaststart option
        Then it is selected

    Scenario Outline: Choose a device, then choose a custom format
        Given I choose a "<device>" conversion option
        When I open the custom pulldown
        Then the "<size>" and "<output format>" of the selected "<device>" is displayed

    Examples:
        | device | size | output format |
        | Galaxy Tab | 1024 x 800 | MP4 h.264 |
        | iPhone 4 | 480 x 320 | MP4 h.264 |
        | PSP | 320 x 480 | MP4 |

    Scenario: Choose a device, then choose a custom size
        Given I choose a "<device>" conversion option
            And I open the custom pulldown
        When I change the size value 
        Then then "<device>" is no longer selected
            And the menu is reset

    Scenario: Choose a device, then choose a custom aspect ratio
        Given I choose a "<device>" conversion option
            And I open the custom pulldown
        When I set the aspect ratio
        Then I'm not really sure what should happen

    Scenario: Size and Aspect ratio selection
        When I set the aspect ratio
        Then there should be some smart way to make sure that the size and aspect ratio values are not conflicting
            And therefore if you have a size selected, and then select an aspect ratio, a valid size should be calculated based on the chosen width and the size value should be updated.

    Scenario: Set the output file location
        When I click on the "Save to" option
        Then I can browse to choose the file output directory

    Scenario Outline: Don't Upsize checkbox is the default for device conversions
        Given I choose a "<device>" conversion option
        When I open the custom pulldown
        Then "Don't Upsize" is selected by default
    
    Examples:
        | device |
        | iPod |
        | Kindle Fire |
        | Galaxy Tab |

    Scenario Outline: Don't Upsize checkbox is the default for custom conversions
        Given I choose a "<custom>" output format
        When I open the custom pulldown
        Then "Don't Upsize" is selected by default

    Examples:
        | custom |
        | webM |
        | MP4 |
        | Theora |
        | AVI |


    Scenario: Remember last settings on restart
        Given I have performed some conversions
        When I choose a new batch of files
        Then My previous conversion settings are selected by default

    Scenario: Remember last settings after restart
        Given I have performed conversions
        When I restart mvc
        Then My previous conversion settings are selected by default

    

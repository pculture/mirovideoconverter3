Feature: Completed conversions
    As a user after I complete a conversion
    I want to be able to locate and play the file
    And it should be formatted as I specified

Scenario: Send to iTunes
    When I convert a file to an Apple format
        And I have Send to iTunes checked
    Then the file is added to my iTunes library

Scenario: File in specific output location
    When I convert a file
        And I have the output directory specified
    Then the output file is in the specified directory

Scenario: File in default output location
    When I convert a file
        And I have the default output directory specified
    Then the output file is in the default directory


Scenario: Output file name
    When I convert a file
    Then is named with the file name (or even better item title) as the base
        And the output container is the extension

Scenario: Output file video size
    When I convert a file to a "<device"> format
    Then the output file is resized correctly

Scenario: Output file framerate
    When I convert a file to a "<device"> format
    Then the output framerate is as close to the original as possible
        But is does not exceed the max framerate supported by the specified device

Scenario: Output ffmpeg output
    Given I convert a file
    When I view the ffmpeg output
    Then the ffmpeg output is displayed in a text window

Scenario: File displays as completed
    When I convert a file
    Then the file displays as completed

Scenario: File fails conversion
    When I convert a file
    And the file conversion fails
    Then the file displays as failed.

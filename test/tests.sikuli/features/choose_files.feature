Feature: Choose files to convert

    Scenario: Choose a single file
        When I browse for a file
        Then it is added to the list of files.

    Scenario: Choose several files
        When I browse for several files
        Then they are added to the list of files

    Scenario: Choose a directory of files
        When I browse to a direcory of files
        Then they are added to the list of files

    Scenario: Drag a single file
        When I drag a file to the drop section
        Then it is added to the list of files

    Scenario: Drag multiple files
        When I drag several files to the drop section
        Then they are added to the list of files

    Scenario: Drag additional files to the existing list
        Given I have files in the list of files
        When I drag a file to the drop section
        Then it is appended to the list of files

    Scenario: Choose additional files and add the to the existing list
        Given I have files in the list of files
        When I browse for several files
        Then they are appended to the list of files

    Scenario: Remove a file from the list of files
        Given I have files in the list of file
        When I remove it from the list
        Then it is not in the list of files

    Scenario: Remove the last file from the list
        Given I have files in the list of file
        When I remove each of them from the list
        Then the list of files is empty

    

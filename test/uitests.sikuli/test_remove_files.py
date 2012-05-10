import sys
import os
import tempfile
import shutil
import unittest
from mvcgui import MVCGui
import datafiles
import devices

data = datafiles.TestData()



class Test_Remove_Files(unittest.TestCase):
    """Remove files from the conversion list

    """

    def setUp(self):
        """
        setup app for tests  

        """
        mvc = MVCGui()
        mvc.mvc_focus()
        print "starting test: ", self.shortDescription()
        datadir, testfiles = data.test_data()
        mvc.browse_for_files(datadir, testfiles)

    def test_remove_a_file(self):
        """Scenario: Remove a file from the list of files.

        Given I have files in the list
        When I remove it from the list
        Then it is not in the list
        """
        
        mvc.mvcGui()
        _, testfiles = data.test_data(many=False)
        item = testfiles[0]
        assert mvc.remove_files(item)

    def test_remove_all_files(self):
        """Scenario: Remove all the files from the list.

        Given I have files in the list
        When I remove them from the list
        Then the list of files is empty
        """
        mvc.mvcGui()
        _, testfiles = data.test_data()
        assert mvc.remove_files(testfiles)

    def test_remove_from_list_with_in_progress_conversions(self):
        """Scenario: Remove a file from the list of files with conversions in progress.

        Given I have files in the list
            And I start conversion
        When I remove it from the list
        Then it is not in the list
        """
        
        item = 'slow_conversion.mkv'
        item_dir = data.testfile_attr(item, 'testdir') 
        mvc.mvcGui()
 
        mvc.browse_for_files(item_dir, item)
        mvc.choose_device_conversion("WebM")
        mvc.start_conversion()

        _, origtestfiles = test_data()
        mvc.remove_files(origtestfiles[1])        
        assert mvc.verify_file_in_list(item)
        assert mvc.verify_completed(item, 160)
 
    def test_remove_last_queued_file_with_in_progress_conversions(self):
        """Scenario: Remove the last queued file from the list with conversions in progress.

        Given I have lots of files files in the list
            And I start conversion
        When I remove the queued file from the list
        Then the in_progress conversions finished.
        """
        item = 'slow_conversion.mkv'
        item_dir = data.testfile_attr(item, 'testdir') 
        mvc.mvcGui()
 
        mvc.browse_for_files(item_dir, item)
        mvc.choose_device_conversion("Theora")
        mvc.start_conversion()
        mvc.remove_queued_conversions()
        assert mvc.verify_conversions_finished()

        



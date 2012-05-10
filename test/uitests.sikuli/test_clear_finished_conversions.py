#!/usr/bin/python

import sys
import os
import tempfile
import shutil
import unittest
from mvcgui import MVCGui
import datafiles
import devices

data = datafiles.TestData()


class Test_Clear_Finished_Conversions(unittest.TestCase):
    """Feature: Removed completed conversions from the list.

       When and item has completed or failed convsion
       I want to remove it from the list
    """

    def setUp(self):
        """
        Each tests assumes that I there are files that have been converted. 

        """
        self.mvc = MVCGui()
        self.mvc.mvc_focus()
        print "starting test: ", self.shortDescription()
        datadir, testfiles = data.test_data()
        self.mvc.browse_for_files(datadir, testfiles)
        self.output_dir = tempfile.mkdtemp()
        self.mvc.choose_save_location(self.output_dir)

    def test_clear_finished_conversions(self):
        """Feature: Clear a finished conversions.
 
        Given I have converted a file
        When I clear finished conversions
        Then the file is removed
        """
        mvc = MVCGui()
        _, testfiles = data.test_data(many=True)
        mvc.start_conversions()
        assert mvc.clear_finished_conversions(testfiles)
        


    def test_clear_finished_item_with_in_progress(self):
        """Scenario: Clear finished conversions while others are in progress.

        Given I have converted a file
            And I have some conversions in progress
        When I clear finished conversions
        Then the completed files are removed
            And the in-progress conversions remain
        """
        _, testfiles = data.test_data(many=True)
        item = 'slow_conversion.mkv'
        item_dir = data.testfile_attr(item, 'testdir')
        mvc = MVCGui()
        mvc.browse_for_files(item_dir, item)
        mvc.start_conversions()
        mvc.clear_finished_conversions(testfiles)
        assert mvc.verify_converting(item)
        

        
    def test_clear_finished_after_conversion_errors(self):
        """Scenario: Clear finished conversions after conversion errors.

           Given I convert several files and 1 that will fail
           When I clear finished conversions
           Then the completed files are removed
             And the failed conversions are removed
        """
        _, testfiles = data.test_data(many=True)
        item = 'fake_video.mp4'
        item_dir = data.testfile_attr(item, 'testdir')
        mvc = MVCGui()
        mvc.browse_for_files(item_dir, item)
        mvc.start_conversions()
        mvc.verify_conversions_finished()
        mvc.clear_and_start_over()
        assert mvc.verify_file_not_in_list(testfiles[0])
        assert mvc.verify_file_not_in_list(item)

    def tearDown(self):
        self.mvc.mvc_quit()
        shutil.rmtree(self.output_dir)


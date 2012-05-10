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


class Test_Conversions(unittest.TestCase):
    """For any completed conversion
    I want to be able to locate and play the file
    And it should be formatted as I have specified
    """

    def setUp(self):
        """
        Each tests assumes that I there are files in the list ready to be converted to some format. 

        """
        self.mvc = MVCGui()
        self.mvc.mvc_focus()
        print "starting test: ", self.shortDescription()
        datadir, testfiles = data.test_data(many=True)
        self.mvc.browse_for_files(datadir, testfiles)
        self.output_dir = tempfile.mkdtemp()
        self.mvc.choose_save_location(self.output_dir)


    def test_send_file_to_itunes(self):
        """Scenario: Send to iTunes.
 
        Given I have "Send to iTunes" checked
        When  I convert the an apple format 
        Then the file is added to my iTunes library
        """
        item = "mp4-0.mp4"
        mvc = MVCGui()
        mvc.choose_device_conversion("iPad")
        mvc.choose_itunes()
        mvc.start_conversions()
        mvc.verify_completed(item, 30)
        assert mvc.verify_itunes(item)
        

    def test_verify_custom_output_directory(self):
        """Scenario: File in specific output location.

        Given I have set the output directory to "directory"
        When I convert a file
        Then the output file is in the specified directory
        """

        custom_output_dir = os.path.join(os.getenv("HOME"),"Desktop")
        item = "mp4-0.mp4"
        mvc.mvcGui()
        mvc.choose_device_conversion("KindleFire")
        mvc.choose_save_location(custom_output_dir)
        mvc.start_conversions()
        mvc.verify_completed(item, 30)
        assert mvc.verify_output_dir(self, item, custom_output_dir)

    def test_file_in_default_location(self):
        """Scenario: File in default output location.

        Given I have set the output directory to "default"
        When I convert a file
        Then the output file is in the default directory
        """

        datadir, testfile = data.test_data()
        item = testfile[0]
        mvc.mvcGui()
        mvc.choose_device_conversion("Galaxy Tab")
        mvc.choose_save_location('default')
        mvc.start_conversions()
        mvc.verify_completed(item, 30)
        assert mvc.verify_output_dir(self, item, datadir)

    def test_output_file_name_in_default_dir(self):
        """Scenario: Output file name when saved in default (same) directory.
        
        When I convert a file
        Then it is named with the file name (or even better item title) as the base
        And the output container is the extension
        """
        self.fail('I do not know the planned naming convention yet')

    def test_output_file_name_in_custom_dir(self):
        """Scenario: Output file name when saved in default (same) directory.
        
        When I convert a file
        Then it is named with the file name (or even better item title) as the base
        And the output container is the extension
        """
        self.fail('I do not know the planned naminig convention yet')

    def test_output_video_no_upsize(self):
        datadir, testfile = data.test_data()
        item = testfile[0] #mp4-0.mp4 is smaller than the Apple Universal Setting
        mvc.mvcGui()
        mvc.choose_device_conversion("Apple Universal")
        mvc.choose_dont_upsize('on')
        mvc.start_conversion()
        assert mvc.verify_size(os.path.join(datadir, item), width, height)


        """Scenario: Output file video size.

        When I convert a file to "format"
        And Don't Upsize is selected
        Then the output file dimensions are not changed if the input file is smaller than the device
        """
        
	##This test is best covered more completely in unittests to verify that we resize according to device sizes
        item = "mp4-0.mp4" #mp4-0.mp4 is smaller than the Apple Universal Setting
        mvc.mvcGui()
        mvc.choose_device_conversion("Apple Universal")
        mvc.choose_dont_upsize('on')
        mvc.start_conversion()
        assert mvc.verify_size(os.path.join(self.output_dir, item), width, height)



    def test_output_video_upsize(self):
        """Scenario: Output file video size.

        When I convert a file to "format"
        And Don't Upsize is NOT selected
        The the output file dimensions are changed to match the device spec.
        """
        
##This test is best covered more completely in unittests to verify that we resize according to device sizes

        item = "mp4-0.mp4" #mp4-0.mp4 is smaller than the Apple Universal Setting
        mvc.mvcGui()
        mvc.choose_device_conversion("Apple Universal")
        mvc.choose_dont_upsize('off')
        mvc.start_conversion()
        assert mvc.verify_size(os.path.join(self.output_dir, item), width, height)

    def test_completed_conversions_display(self):
        """Scenario: File displays as completed.

        When I convert a file
        Then the file displays as completed
        """
        item = "mp4-0.mp4"
        mvc.mvcGui()
        mvc.choose_device_conversion("Xoom")
        mvc.choose_save_location(custom_output_dir)
        mvc.start_conversions()
        assert mvc.verify_completed(item, 30)


    def test_failed_conversion_display(self):
        """Scenario: File fails conversion.
        When I convert a "file" to "format"
            And the file conversion fails
        Then the file displays as failed.
        """
        item = 'fake_video.mp4'
        item_dir = data.testfile_attr(item, 'testdir')
        mvc.mvcGui()
        mvc.browse_for_files(item_dir, item)
        mvc.choose_device_conversion("iPhone")
        mvc.start_conversion()
        assert mvc.verify_failed(item)


    def test_ffmpeg_log_output_on_failure(self):
        """Scenario: Show ffmpeg output.

        Given I convert a file
        When I view the ffmpeg output
        Then the ffmpeg output is displayed in a text window
        """
        item = 'fake_video.mp4'
        item_dir = data.testfile_attr(item, 'testdir')
        mvc.mvcGui()
        mvc.browse_for_files(item_dir, item)
        mvc.choose_device_conversion("iPhone")
        mvc.start_conversion()
        mvc.verify_failed(item)
        assert mvc.show_ffmpeg_output(item)
        

    def tearDown(self):
        shutil.rmtree(self.output_dir)
        self.mvc_quit()
        

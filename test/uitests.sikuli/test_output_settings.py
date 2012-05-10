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


class Test_Custom_Settings(unittest.TestCase):
    """Features: users can specify custom format, size and aspect ration.
  
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

    def choose_custom_size(self):
        """Scenario: Choose custom size.

        When I enter a custom size option
        Then the conversion uses that setting."""
        mvc = MVCGui()
        _, testfiles = data.test_data()
        item = testfiles[0]
        w = '360'
        h = '180'

        mvc.choose_custom_size(self, 'on', width=w, height=h)
        mvc.mvc.choose_device_conversion('WebM')
        mvc.start_conversions()
        assert mvc.verify_size(item, width=w, height=h)                


    def choose_aspect_ration(self):
        """Scenario: Choose a device, then choose a custom aspect ratio.

        Given  I choose a device option
        When I set the "aspect ratio"
        Then I'm not really sure what will happen
        """
        self.fail('need to know how to test this')

    def choose_device_then_change_size(self):
        """Scenario: Choose a device, then choose a custom size.

        When  I choose a device 
        And I change size
        Then the selected size is used in the conversion
        """
        mvc = MVCGui()
        _, testfiles = data.test_data()
        item = testfiles[0]
        w = '240'
        h = '180'
        mvc.choose_device_conversion('Galaxy Tab')
        mvc.choose_custom_size(self, 'on', width=w, height=h)
        mvc.start_conversions()
        assert mvc.verify_size(item, width=w, height=h) 
 

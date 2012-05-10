#!/usr/bin/python

import devices
from sikuli.Sikuli import *
import devices
import config
from mvcgui import MVCGui
import datafiles

data = datafiles.TestData()

def test_other_conversions():
    """Scenario: test other output conversion options.
   
    """
    device_list = devices.devices('Other')
    for x in device_list:
        yield convert_to_format, x

def convert_to_format(device_output):
    print device_output
    expected_failures = ['fake_video.mp4']
    mvc = MVCGui()
    mvc.mvc_focus()
    datadir, testfiles = data.test_data(many=True, new=True)
    mvc.browse_for_files(datadir, testfiles)
    output_dir = tempfile.mkdtemp()
    mvc.choose_save_location(output_dir)
    mvc.choose_device_conversion("device_output")
    mvc.start_conversions()
    for item in testfiles:
        if item in expected_failures:
            mvc.verify_failed(item, 120)
        else:
            mvc.verify_completed(item, 120)
        mvc.clear_finished_files(item)
    mvc.clear_and_start_over()

       

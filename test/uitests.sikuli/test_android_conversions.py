#!/usr/bin/python

import devices
from sikuli.Sikuli import *
import devices
import config
from mvcgui import MVCGui
import datafiles
data = datafiles.TestData()

def test_android_conversions():
    """Scenario: test each android conversion option.
   
    """
    device_list = devices.devices('Android')
    for x in device_list:
        yield convert_to_format, x


def test_android_size_output_default():
    """Scenario: the output format and size are defaults when device selected.

    """
    device_list = devices.devices('Android')
    datadir, testfiles = data.test_data(many=True, new=True)
    mvc = MVCGui()
    mvc.mvc_focus()
    mvc.browse_for_files(datadir, testfiles)

    for x in device_list:
        yield device_defaults, x, mvc


def device_defaults(device_output, mvc):
    print device_output
    mvc.choose_device_conversion(device_output)
    width = device.device_attr(device_output, 'width')
    height = device.device_attr(device_output, 'height')
    default_format = 'MP4'
    assert mvc.verify_device_format_selected(device_output)
    assert mvc.verify_device_size_default(str(width), str(height))
    


def convert_to_format(device_output):
    """Scenario: Test items are converted to the specified format.
    """
    print device_output
    mvc = MVCGui()
    mvc.mvc_focus()
    expected_failures = ['fake_video.mp4']
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

       

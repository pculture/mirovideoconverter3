# -*- coding: utf-8 -*-
from lettuce import step
from lettuce import world
import datafiles
import devices

data = datafiles.TestData()
DEFAULT_DEVICE = "iPad"

def test_data(many=False, new=False):
    UNITTESTFILES = ['mp4-0.mp4', 'webm-0.webm', 'drm.m4v']
    SIKTESTFILES = ['baby_block.m4v', 'story_styff.mov']
    if new:
        TESTFILES = SIKTESTFILES
    else:
        TESTFILES = UNITTESTFILES

    DATADIR = data.testfile_attr(TESTFILES[0], 'testdir')

    if not many:
        TESTFILES = TESTFILES[:1]

    print TESTFILES
    return DATADIR, TESTFILES
       
def device_group(option):
    menu_group = devices.dev_attr(option, 'group')
    return menu_group

def device_output(option):
    dev_output_format = devices.dev_attr(option, 'container')
    return device_output_format
    

@step('I browse for (?:a|several)( new)? file(s)?')
def browse_for_files(step, new, several): # file or files determines 1 or many
    datadir, testfiles = test_data(several, new)
    print testfiles
    world.mvc.browse_for_files(datadir, testfiles)

@step('The( new)? file(s)? (?:is|are) added to the list')
def files_added_to_the_list(step, new, several):
    _, testfiles = test_data(several, new)
    for t in testfiles:
        assert world.mvc.verify_file_in_list(t) 
    
@step('I browse to a directory of files')
def add_a_directory(step):
    datadir, _ = test_data(many=True)
    world.mvc.add_directory_of_files(datadir)

@step(u'When I drag (?:a|several)( new)? file(s)? to the drop zone')
def drag_to_the_drop_zone(step, new, several):
    datadir, testfiles = test_data(several, new)
    world.mvc.drag_and_drop_files(datadir, testfiles)


@step('Given I have files in the list')
def given_i_have_some_files(step):
    step.given('I browse for several files')

@step('I start conversion')
def start_conversion(step):
    world.mvc.start_conversions()

@step('I remove "([^"]*)" from the list')
def when_i_remove_it_from_the_list(step, items):
    if items == "it":
        _, testfile = test_data()
    elif items == "them":
        _, testfile = test_data(True, False)
    else:
        testfile = items.split(', ')
    world.mvc.remove_files(testfile)

@step('"([^"]*)" is not in the list')
def not_in_the_list(step, items):
    if items == "it":
        _, testfile = test_data()
    assert False, world.mvc.verify_file_in_list(testfile)

@step('I remove each of them from the list')
def i_remove_each_of_them_from_the_list(step):
    assert False, 'This step must be implemented'

@step(u'Then the list of files is empty')
def then_the_list_of_files_is_empty(step):
    assert False, 'This step must be implemented'

@step('I have converted (?:a|some) file(s)?')
def have_converted_file(step, amount):
    if amount == None:
        browse_file = ('I browse for a file') #file or files determines 1 or many
    else:
        browse_file = ('I browse for some files')
    step.given(browse_file)
    step.given('I choose the "test_default" device option')
    step.given('I start conversion')


@step('I clear finished conversions')
def clear_finished_conversions(step, testfiles):
    world.mvc.clear_finished_files()


@step('I (?:convert|have converted) "(.*?)" to "(.*?)"')
def convert_file_to_format(step, filename, device):
   datadir = data.testfile_attr(filename, 'testdir')
   world.mvc.browse_for_files(datadir, [filename])
   world.mvc.choose_device_conversion(device)
   world.mvc.start_conversions()



@step('the "(.*?)" (?:is|are) removed')
def file_is_removed(step, testfile):
    if testfile == "file":
        _, testfile = test_data()        
    assert world.mvc.verify_file_not_in_list(testfile) 

@step('And I have some conversions in progress')
def and_i_have_some_conversions_in_progress(step):
    assert False, 'This step must be implemented'

@step('the completed files are removed')
def completed_files_are_removed(step):
    assert world.mvc.verify_completed_removed() 

@step('the in-progress conversions remain')
def and_the_in_progress_conversions_remain(step):
    assert world.mvc.verify_in_progress()

@step('"(.*?)" is a failed conversion')
def have_failed_conversion(step, item):
    assert verify_failed(self, item) 

@step('the failed conversions are removed')
def failed_conversions_removed(step):
    assert world.mvc.verify_failed_removed() 

@step('I choose the custom size option')
def change_custom_size(step):
    world.mvc.choose_custom_size('on', '150', '175')
    assert world.mvc.verify_test_img('_custom_size_test')

@step('I choose the aspect ratio')
def when_i_choose_the_aspect_ratio(step):
    assert False, 'This step must be implemented'

@step('I choose the "([^"]*)" (?:device|format) option')
def choose_conversion_format(step, device):
    if device == 'test_default':
        device = DEFAULT_DEVICE
    world.mvc.choose_device_conversion(device)


@step('I open the custom pulldown')
def open_custom_pulldown(step):
    world.mvc.open_custom_menu()

@step('I verify "([^"]*)" and "([^"]*)" size setting entry')
def verify_the_size_value(step, width, height):
    assert False, 'This step must be implemented'

@step('I verify the "([^"]*)" (?:device|format)( not)? selected')
def verify_format_selection_for_device(self, device, removed):
    if removed:
        assert False, world.mvc.verify_device_format_selected(device)
    else:
        assert world.mvc.verify_device_format_selected(device)


@step('the menu is reset')
def menu_is_reset(step):
    assert False, 'This step must be implemented'

@step(u'Then there should be some smart way to make sure that the size and aspect ratio values are not conflicting')
def then_there_should_be_some_smart_way_to_make_sure_that_the_size_and_aspect_ratio_values_are_not_conflicting(step):
    assert False, 'This step must be implemented'

@step(u'And therefore if you have a size selected, and then select an aspect ratio, a valid size should be calculated based on the chosen width and the size value should be updated.')
def and_therefore_if_you_have_a_size_selected_and_then_select_an_aspect_ratio_a_valid_size_should_be_calculated_based_on_the_chosen_width_and_the_size_value_should_be_updated(step):
    assert False, 'This step must be implemented'



@step(u'When I restart mvc')
def when_i_restart_mvc(step):
    assert False, 'This step must be implemented'

@step('I have Send to iTunes checked')
def and_i_have_send_to_itunes_checked(step):
    assert False, 'This step must be implemented'

@step('the file is added to my iTunes library')
def file_added_to_itunes(step):
    assert False, 'This step must be implemented'

@step(u'And I have the (default)? output directory specified')
def and_i_have_the_output_directory_specified(step, default):
    assert False, 'This step must be implemented'

@step('the output file is in the (specified|default) directory')
def output_file_specified_directory(step):
    assert False, 'This step must be implemented'


@step(u'Then is named with the file name (or even better item title) as the base')
def then_is_named_with_the_file_name_or_even_better_item_title_as_the_base(step):
    assert False, 'This step must be implemented'

@step(u'And the output container is the extension')
def and_the_output_container_is_the_extension(step):
    assert False, 'This step must be implemented'

@step(u'Then the output file is resized correctly')
def then_the_output_file_is_resized_correctly(step):
    assert False, 'This step must be implemented'


@step(u'When I view the ffmpeg output')
def when_i_view_the_ffmpeg_output(step):
    assert False, 'This step must be implemented'

@step('the ffmpeg output is displayed in a text window')
def then_the_ffmpeg_output_is_displayed_in_a_text_window(step):
    assert False, 'This step must be implemented'


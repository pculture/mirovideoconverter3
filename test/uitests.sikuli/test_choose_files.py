import sys
import os
import tempfile
import shutil
import unittest
from mvcgui import MVCGui
import datafiles
import devices

data = datafiles.TestData()


class Test_Choose_Files(unittest.TestCase):
    """Add files to the conversion list either via browse or drag-n-drop.

    """

    def setUp(self):
        """
        setup app for tests  

        """
        self.mvc = MVCGui()
        self.mvc.mvc_focus()
        print "starting test: ", self.shortDescription()
        self.output_dir = tempfile.mkdtemp()
        self.mvc.choose_save_location(self.output_dir)



    def test_browse_for_a_file(self):
        """Scenario: Browse for a single file.

        When I browse for a file
        Then the file is added to the list
        """
        mvc = MVCGui()
        datadir, testfiles = data.test_data(many=False)
        mvc.browse_for_files(datadir, testfiles)
        item = testfiles[0]
        assert mvc.verify_file_in_list(item) 
      



    def test_choose_several_files(self):
        """Scenario: Browse for several files.

        When I browse for several files
        Then the files are added to the list 
        """
        mvc = MVCGui()
        datadir, testfiles = data.test_data(many=True)
        mvc.browse_for_files(datadir, testfiles)
        for t in testfiles:
            assert mvc.verify_file_in_list(t) 

    def skip_test_choose_a_directory_files(self):
        """Scenario: Choose a directory of files.

        When I browse to a directory of files
        Then the files are added to the list
        """

    def test_drag_a_file_to_drop_zone(self):
        """Scenario: Drag a single file to drop zone.

        When I drag a file to the drop zone 
        Then the file is added to the list 
        """
        mvc = MVCGui()
        datadir, testfiles = data.test_data(many=False)
        mvc.drag_and_drop_files(datadir, testfiles)
        item = testfiles[0]
        assert mvc.verify_file_in_list(item) 

    def test_drag_and_drop_multiple_files(self):
        """Scenario: Drag multiple files.

        When I drag several files to the drop zone 
        Then the files are added to the list
        """
        mvc = MVCGui()
        datadir, testfiles = data.test_data(many=True)
        mvc.drag_and_drop_files(datadir, testfiles)
        for t in testfiles:
            assert mvc.verify_file_in_list(t) 

    def test_drag_more_files_to_drop_zone(self):
        """Scenario: Drag additional files to the existing list.

        Given I have files in the list
        When I drag a new file to the drop zone
        Then the new file is added to the list
        """
        mvc = MVCGui()
        datadir, testfiles = data.test_data(many=True)
        mvc.browse_for_files(datadir, testfiles)
        moredatadir, moretestfiles = data.test_data(many=False, new=True)
        item = testfiles[0]
        mvc.drag_and_drop_files(moredatadir, item)
        assert mvc.verify_file_in_list(item) 

    def test_browse_for_more_files_and_add_them(self):
        """Scenario: Choose additional files and add to the existing list.

        Given I have files in the list of files
        When I browse for several new files
        Then the new files are added to the list
        """

        mvc = MVCGui()
        datadir, testfiles = data.test_data(many=True)
        mvc.browse_for_files(datadir, testfiles)
        moredatadir, moretestfiles = data.test_data(many=False, new=True)
        item = testfiles[0]
        mvc.browse_for_files(moredatadir, item)
        assert mvc.verify_file_in_list(item) 

        
    def test_drag_more_file_while_converting(self):
        """Scenario: Drag additional files to the existing list with conversions in progress.

        Given I have files in the list
            And I start conversion
        When I drag a new file to the drop zone 
        Then the new file is added to the list and is converted
        """

        mvc = MVCGui()
        datadir, testfiles = data.test_data(many=True)
        mvc.browse_for_files(datadir, testfiles)
        mvc.choose_device_conversion("iPad")
        mvc.start_conversion()

        moredatadir, moretestfiles = data.test_data(many=False, new=True)
        item = testfiles[0]
        mvc.drag_and_drop_files(moredatadir, item)
        assert mvc.verify_file_in_list(item)
        assert mvc.verify_completed(item, 60)

    def test_browse_more_files_while_converting(self):
        """Scenario: Choose additional files and add to list with conversions in progress.

        Given I have files in the list
            And I start conversion
        When I browse for several new files
        Then the new files are added to the list
        """

        mvc = MVCGui()
        datadir, testfiles = data.test_data(many=True)
        mvc.browse_for_files(datadir, testfiles)
        mvc.choose_device_conversion("iPad")
        mvc.start_conversion()

        moredatadir, moretestfiles = data.test_data(many=False, new=True)
        item = testfiles[0]
        mvc.browse_for_files(moredatadir, item)
        assert mvc.verify_file_in_list(item)
        assert mvc.verify_completed(item, 60)

    def tearDown(self):
        shutil.rmtree(self.output_dir)
        self.mvc_quit()


from sikuli.Sikuli import *
import devices
import config


class MVCGui(object):

#       ** APP UI IMAGES **

#   ADD FILES
    _INITIAL_DROP_ZONE = 'fresh_start_dropzone.png'
    _CHOOSE_FILES = 'choose_a_file.png'
    _DROP_ZONE = 'file_drop_zone.png'
    _CONVERSIONS_FINISHED = 'conversions_finished.png'


#   BIG BOTTOM BUTTONS
    _START_CONVERSION = 'convert_now.png'
    _STOP_CONVERSION = 'stop_all.png'
    _RESET = 'clear_and_start_over.png'

#       INDIVIDUAL FILE OPTIONS
        #processing
    _IN_PROGRESS = 'progress_bar.png'
    _DELETE_FILE = 'delete_icon.png'
    _CLEAR_FINISHED = 'clear_finished.png'
    _CONVERSION_COMPLETE = 'completed.png'
    _CONVERSION_FAILED = 'failed.png'
    _PAUSE = 'pause_button.png'
    _RESUME = 'resume_button.png'
    _QUEUED = 'queued.png'
    _ERROR = 'error_icon.png'
    _SHOW_FILE = 'show_file.png'

#       CONVERSION OPTIONS SECTION
    _SEND_ITUNES = 'send_to_itunes.png'
    _APPLE_MENU = 'apple_dropdown.png'
    _ANDROID_MENU = 'android_dropdown.png'
    _OTHER_MENU = 'other_dropdown.png'
    _CUSTOM_MENU = 'custom_menu.png'

#       CUSTOM MENU OPTIONS
    _PREFS_CHECKBOX_CHECKED = 'checkbox_checked.png'
    _PREFS_CHECKBOX_UNCHECKED = 'checkbox_unchecked.png'
    _SAVE_TO_OPTION = 'save_to_pulldown.png'
    _OUTPUT_DIRECTORY = 'default_dir_selected.png'
    _SAVE_TO_DEFAULT = 'save_to_default_selected.png'
    _CONVERT_TO_OPTION = 'convert_to_menu.png'
    _CUSTOM_SIZE = 'custom_size.png'
    _WIDTH = 'custom_width.png'
    _HEIGHT = 'custom_height.png'
    _UPSIZE = 'dont_upsize'
    _ASPECT = 'custom_aspect.png'
    _ASPECT_43 = '43_aspect.png'
    _ASPECT_32 = '32_aspect.png'
    _ASPECT_169 = '169_aspect.png'

#       SELECTED CONVERSION OPTION
    _APPLE_SELECTED = 'apple_selected.png'
    _ANDROID_SELECTED = 'android_selected.png'

#       SYSTEM UI
    _SYS_TEXT_ENTRY_BUTTON = 'type_a_filename.png'

#   TEST IMAGES for VERIFICATION
    _custom_size_test = '150x175size.png'
               
    def __init__(self):
        '''
        Constructor
        '''
        config.set_image_dirs()
        self.os_name = config.get_os_name()
#        CMD or CTRL Key
        if self.os_name == 'osx':
            self.CMDCTRL = Key.CMD
        else:
            self.CMDCTRL = Key.CTRL
        
    def mvc_focus(self):
        App.focus("Miro Video Converter")

    def mvc_quit(self):
        App.close("Miro Video Converter")

    def item_region(self, item):
        find(item)
        reg = Region.getLastMatch()
        item_reg = Region(reg.x - 30, reg.y - 30, 400, 50)
        return(item_reg)

    def choose_directory(self, dirname):
        self.type_a_path(dirname)

    def type_a_path(self, dirname):
        if config.get_os_name() == "win":
            if not exists("Location",5):
                click(self.SYS_TEXT_ENTRY_BUTTON)
                time.sleep(2)
        type(dirname +"\n")
        type(Key.ENTER)

    def browse_for_files(self, dirname, testdata):
        click(Pattern(self._CHOOSE_FILES))
        time.sleep(2) #osx freaks out if you start typing too fast
        self.type_a_path(dirname)
        keyDown(self.CMDCTRL)
        for f in testdata:
            click(f)
        keyUp(self.CMDCTRL)

    def add_directory_of_files(self, dirname):
        click(self._CHOOSE_FILES)
        self.choose_directory(dirname)
        type(Key.ENTER)

    def drag_and_drop_files(self, dirname, testdata):
        click(self._CHOOSE_FILES)
        y = getLastMatch() # y is drop destination
        type(dirname)
        type(Key.ENTER)
        keyDown(self.CMDCTRL)
        for f in testdata: 
            find(f)
            x = getLastMatch() # the drag start is the last file we find and select
            click(getLastMatch())
        dragDrop(x, y)
        keyUp(self.CMDCTRL)
        type(Key.ESC) #close the file browser dialog
        

    def remove_files(self, *items):
        for item in items:
            r = self.item_region(item)
            r.click(self._DELETE_FILE)
            assert r.waitVanish(item)

    def start_conversions(self):
        click(self._START_CONVERSION)

    def stop_conversions(self):
        click(self._STOP_CONVERSION)

    def clear_and_start_over(self):
        click(self._RESET)

    def pause_conversions(self, *items):
        for item in items:
            r = self.item_region(item)
            r.click(self._PAUSE)
            assert r.exists(self._RESUME)

    def clear_finished_files(self, items, wait=30):
        """Clears out the completed individual conversions.

        """
        for item in items:
            r = self.item_region(item)
            r.exists(self._CLEAR_FINISHED, wait)
            click(r.getLastMatch())
            assert waitVanish(item, 2)

    def show_file(self, item):
        for item in items:
            r = self.item_region(item)
            r.click(self._SHOW_FILE)
            # FIXME Verify the file is there and close the window
       

    def choose_device_conversion(self, device):
        device_group = devices.dev_attr(device, 'group')
        menu_img = getattr(self, "".join(["_",device_group.upper(),"_","MENU"]))
        click(menu_img)
        click(device)


    def open_custom_menu(self):
        if not exists(self._OUTPUT_DIRECTORY):
            click(self._CUSTOM_MENU)

    def choose_save_location(self, location='default'):
        self.open_custom_menu()
        if location == 'default' and not exists(self._SAVE_TO_DEFAULT):
            click(self._SAVE_TO_OPTION)
            click(self._SAVE_TO_DEFAULT)
        else:
            click(self._SAVE_TO_OPTION)
            self.choose_directory(location)

    def set_pref_checkbox(self, option, setting):
        """Check or uncheck the box for a preference setting.
           Valid values are ['on' and 'off']

        """
        valid_settings = ['on', 'off']
        if setting not in valid_settings:
            print("valid setting value not proviced, must be 'on' or 'off'")
        #CHECK THE BOX
        pref_image = getattr(self, "".join(["_",option]))
        find(pref_image)
        reg = Region(getLastMatch())
        box = Region(reg.getX()-15, sr_loc.getY()-10, pref_reg.getW(), 30) #location of associated checkbox
        if setting == "off":
            if box.exists(self._PREFS_CHECKBOX_CHECKED):
                click(box.getLastMatch())
        if setting == "on":
            if box.exists(self._PREFS_CHECKBOX_NOT_CHECKED):
                click(box.getLastMatch())
    
    def choose_custom_size(self, setting, width=None, height=None):
        self.open_custom_menu(self)
        if not width or not height:
            setting = 'off'
        self.set_pref_checkbox(self._CUSTOM_SIZE, setting)
        if setting == 'on':
            type(Key.TAB)
            type(width)
            type(Key.TAB)
            type(height) 
        
    def choose_dont_upsize(self, setting):
        self.open_custom_menu(self)
        self.set_pref_checkbox(self._UPSIZE, setting)

    def choose_aspect_ratio(self, setting, ratio=None):
        self.open_custom_menu(self)
        if ratio == None:
            setting = 'off'
        self.set_pref_checkbox(self._ASPECT, setting)
        if setting == 'on':
            ratio_img = getattr(self, "".join(["_", "ASPECT", ratio]))
            click(ratio_img)

    def choose_format(self, output):
        self.open_custom_menu(self)
        mouseMove(self._CONVERT_TO_OPTION.right(30))
        mouseDown(Button.LEFT)
        mouseMove(output)
        mouseUp(Button.LEFT)

    def choose_itunes(self, setting):
        self.set_pref_checkbox(self._SEND_ITUNES, setting)


    def remove_queued_conversions(self):
        while exists(self._QUEUED):
            qreg = Region(getLastMatch())
            q_item = Region(reg.getX()+30, sr_loc.getY()-20, 500, 30)
            q_item.click(self._DELETE_FILE)

    def verify_device_format_selected(self, device):
        device_group = devices.dev_attr(device, 'group')
        if device_group == 'Format':
            if exists(device):
                return True
        else:
            if exists(device) and exists("MP4"): #all devices are mp4 by default
                return True
 

    def verify_size(self, item, width, height):
        self.show_ffmpeg_output(item)
        expected_size_parameter = "-s "+width+"x"+height
        type(self.CMDCTRL, 'f')
        type('-s '+width+'x'+'height')
        type(self.CMDCTRL, 'c') #copy the ffmpeg size command to the clipboard
        size_param = Env.getClipboard()
        if size_param == expected_size_parameter:
            return True
     


    def verify_device_size_default(self, width, height):
        self.open_custom_menu()
        self.set_pref_checkbox(self._CUSTOM_SIZE, setting)
        click('Width')
        type(self.CMDCTRL)
        displayed_width = Env.getClipboard()
        click('Height')
        type(self.CMDCTRL)
        displayed_height = Env.getClipboard()
        if displayed_height == height and displayed_width == width:
            return True


    def verify_converting(self, item):
        r = self.item_region(item)
        if r.exists(self._IN_PROGRESS):
            return True

    def verify_paused(self, item):
        r = self.item_region(item)
        if r.exists(self._RESUME):
            return True

    def verify_completed(self, item, wait=10):
        """Verify an individual conversion has completed.

        """
        r = self.item_region(item)
        if r.exists(self._CONVERSION_COMPLETE, wait):
            return True

    def verify_completed_removed(self):
        if not exists(self._CONVERSION_COMPLETE):
            return True

    def verify_conversions_finished(self):
        """This verifies the entire group of conversions are complete.

       """
        if exists(self._CONVERSIONS_FINISHED):
            return True

    def verify_failed(self, item, wait=20):
        r = self.item_region(item)
        try:
            r.exists(self._CONVERSION_FAILED, wait)
            return True
        except:
            return False

    def verify_failed_removed(self):
        if not exists(self._CONVERSION_FAILED):
            return True

    def verify_file_in_list(self, item):
        r = self.item_region(item)
        if r.exists(item):
            return True

    def verify_file_not_in_list(self, item):
        if not exists(item):
            return True  

    def verify_queued(self, item):
        r = self.item_region(item)
        if r.exists(self._QUEUED):
            return True

    def verify_in_progress(self, item=None):
        if item: 
            r = self.item_region(item)
            if r.exists(self._IN_PROGRESS): return True
        else:
            if exists(self._IN_PROGRESS): return True

    def verify_itunes(self, item):
        pass

    def verify_output_dir(self, item, directory):
        r = self.item_region(item)
        r.click(self._SHOW_FILE)
        type(Key.ESC)

        #FIXME need to get what the output name is going to be.
        output_file = os.path.join(directory, item)  
        if os.path.isfile(output_file):
            return True


    def show_ffmpeg_output(self, item):
        r = self.item_region(item)
        self.verify_completed(item, 30)

        r.click(self._SHOW_FFMPEG)
        if exists("STARTING CONVERSION"):
            return True
      



   

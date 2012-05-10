#config.py
import os
import time
from sikuli.Sikuli import *


def set_image_dirs():
    """Set the Sikuli image path for the os specific image directory and the main Image dir.

    """
    os_imgs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Images_"+get_os_name())
    imgs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Images")

    dir_list = [imgs, os_imgs]
    #Add the image dirs to the sikuli search path if it is not in there already   
    for d in dir_list:
        if d not in list(getImagePath()):
            addImagePath(d)
       
def get_os_name():
    """Returns the os string for the SUT
    """
    if "MAC" in str(Env.getOS()):
        return "osx"
    elif "WINDOWS" in str(Env.getOS()):
        return "win"
    elif "LINUX" in str(Env.getOS()):
        return "lin"
    else:
        print ("I don't know how to handle platform '%s'", Env.getOS())


def launch_cmd():
    """Returns the launch path for the application.

    launch is an os specific command
    """
    if get_os_name() == "osx":
        launch_cmd =  "/Applications/Miro Video Converter.app"
    elif get_os_name() == "win":
        launch_cmd = os.path.join(os.getenv("PROGRAMFILES"),"Participatory Culture Foundation","Miro Video Converter","MiroConverter.exe")
    else:
        print get_os_name()
    print launch_cmd
    return launch_cmd



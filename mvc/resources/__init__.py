import os.path

from mvc.widgets.osx import resource_path

def image_path(name):
    return os.path.join(resource_path(), name)

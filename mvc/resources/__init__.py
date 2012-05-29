import os.path

def image_path(name):
    return os.path.join(os.path.dirname(__file__), 'images', name)

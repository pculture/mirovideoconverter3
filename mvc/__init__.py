from mvc import converter, conversion, video

class Application(object):

    def __init__(self):
        self.converter_manager = converter.ConverterManager()
        self.conversion_manager = conversion.ConversionManager()
        self.started = False

    def startup(self):
        if self.started:
            return
        self.converter_manager.startup()
        self.started = True

    def start_conversion(self, filename, converter_id):
        self.startup()
        converter = self.converter_manager.get_by_id(converter_id)
        v = video.VideoFile(filename)
        return self.conversion_manager.start_conversion(v, converter)

    def run(self):
        raise NotImplementedError

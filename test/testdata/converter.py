from mvc.converter import ConverterInfo

class TestConverterInfo(ConverterInfo):
    media_type = 'video'
    extension = 'test'
    bitrate = 10000

    def get_executable(self):
        return '/bin/true'

    def get_arguments(self, video, output):
        return [video.filename, output]

    def process_status_line(self, line):
        return {'finished': True}


converters = [TestConverterInfo('Test Converter')]

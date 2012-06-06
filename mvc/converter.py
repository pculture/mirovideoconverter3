import logging
from glob import glob
import json
import re
import os.path

from mvc import settings, utils
from mvc.utils import hms_to_seconds

logger = logging.getLogger(__name__)

NON_WORD_CHARS = re.compile(r"[^a-zA-Z0-9]+")

class ConverterInfo(object):
    media_type = None
    bitrate = None
    extension = None

    def __init__(self, name):
        self.name = name
        self.identifier = NON_WORD_CHARS.sub("", name).lower()

    def get_executable(self):
        raise NotImplementedError

    def get_arguments(self, video, output):
        raise NotImplementedError

    def get_output_filename(self, video):
        basename = os.path.basename(video.filename)
        name, ext = os.path.splitext(basename)
        return '%s.%s.%s' % (name, self.identifier, self.extension)

    def get_output_size_guess(self, video):
        if not self.bitrate or not video.duration:
            return None
        if video.duration:
            return self.bitrate * video.duration / 8

    def process_status_line(self, line):
        raise NotImplementedError

class FFmpegConverterInfoBase(ConverterInfo):
    DURATION_RE = re.compile(r'\W*Duration: (\d\d):(\d\d):(\d\d)\.(\d\d)'
                             '(, start:.*)?(, bitrate:.*)?')
    PROGRESS_RE = re.compile(r'(?:frame=.* fps=.* q=.* )?size=.* time=(.*) '
                             'bitrate=(.*)')
    LAST_PROGRESS_RE = re.compile(r'frame=.* fps=.* q=.* Lsize=.* time=(.*) '
                                  'bitrate=(.*)')

    extension = None

    def get_executable(self):
        return settings.get_ffmpeg_executable_path()

    def get_arguments(self, video, output):
        return (['-i', video.filename, '-strict', 'experimental'] +
                self.get_extra_arguments(video, output) + [output])

    def get_extra_arguments(self, video, output):
        raise NotImplementedError

    @staticmethod
    def _check_for_errors(line):
        if line.startswith('Unknown'):
            return line
        if line.startswith("Error"):
            if not line.startswith("Error while decoding stream"):
                return line

    @classmethod
    def process_status_line(klass, video, line):
        error = klass._check_for_errors(line)
        if error:
            return {'finished': True, 'error': error}

        match = klass.DURATION_RE.match(line)
        if match is not None:
            hours, minutes, seconds, centi = [
                int(m) for m in match.groups()[:4]]
            return {'duration': hms_to_seconds(hours, minutes,
                                               seconds + 0.01 * centi)}

        match = klass.PROGRESS_RE.match(line)
        if match is not None:
            t = match.group(1)
            if ':' in t:
                hours, minutes, seconds = [float(m) for m in t.split(':')[:3]]
                return {'progress': hms_to_seconds(hours, minutes, seconds)}
            else:
                return {'progress': float(t)}

        match = klass.LAST_PROGRESS_RE.match(line)
        if match is not None:
            return {'finished': True}


class FFmpegConverterInfo(FFmpegConverterInfoBase):

    parameters = None

    def __init__(self, name, (width, height)):
        self.width, self.height = width, height
        ConverterInfo.__init__(self, name)

    def get_extra_arguments(self, video, output):
        if self.parameters is None:
            raise NotImplementedError
        width, height = utils.rescale_video((video.width, video.height),
                                            (self.width, self.height))
        ssize = '%ix%i' % (width, height)
        return self.parameters.format(
            ssize=ssize,
            input=video.filename,
            output=output).split()


class FFmpeg2TheoraConverterInfo(ConverterInfo):
    media_type = 'video'
    bitrate = 1200000
    extension = 'ogv'

    video_quality = 8
    audio_quality = 6

    def __init__(self, name):
        ConverterInfo.__init__(self, name)
        self.line_progress = {}

    def get_executable(self):
        return settings.get_ffmpeg2theora_executable_path()

    def get_arguments(self, video, output):
        return ('--videoquality', str(self.video_quality),
                '--audioquality', str(self.audio_quality),
                '--frontend',
                '-o', output, video.filename)

    def process_status_line(self, video, line):
        # line_progress is a hack because sometimes FFmpeg2theora sends us a
        # JSON object over multiple lines.  If we can't parse the object, we
        # start throwing caching the previous lines and wait until we get a
        # whole object.
        if video in self.line_progress:
            self.line_progress[video].append(line)
            try:
                parsed = json.loads("".join(self.line_progress[video]))
            except ValueError:
                return
            else:
                del self.line_progress[video]
        else:
            try:
                parsed = json.loads(line)
            except ValueError:
                self.line_progress[video] = [line]
                return

        if 'result' in parsed:
            if parsed['result'] == 'ok':
                return {'finished': True}
            else:
                return {'finished': True,
                        'error': parsed['result']}
        elif 'error' in parsed:
            return {'finished': True,
                    'error': parsed['error']}
        else:
            return {
                'duration': parsed['duration'],
                'progress': parsed['position'],
                'eta': parsed['remaining']
                }

class ConverterManager(object):
    def __init__(self):
        self.converters = {}

    def add_converter(self, converter):
        self.converters[converter.identifier] = converter

    def startup(self):
        resources_path = os.path.join(os.path.dirname(__file__), 'resources',
                                      '*.py')
        self.load_converters(resources_path)

    def load_converters(self, path):
        converters = glob(path)
        for converter_file in converters:
            global_dict = {}
            execfile(converter_file, global_dict)
            if 'converters' in global_dict:
                [self.add_converter(converter) for converter in
                 global_dict['converters']]
                logger.info('load_converters: loaded %i from %r',
                            len(global_dict['converters']),
                            converter_file)

    def list_converters(self):
        return self.converters.values()

    def get_by_id(self, id_):
        return self.converters[id_]

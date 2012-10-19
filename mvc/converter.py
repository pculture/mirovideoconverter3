import json
import logging
import os
import re
import shutil

from mvc import resources, settings, utils
from mvc.utils import hms_to_seconds

from mvc.qtfaststart import processor
from mvc.qtfaststart.exceptions import FastStartException

logger = logging.getLogger(__name__)

NON_WORD_CHARS = re.compile(r"[^a-zA-Z0-9]+")

class ConverterInfo(object):
    """Describes a particular output converter

    ConverterInfo is the base class for all converters.  Subclasses must
    implement get_executable() and get_arguments()

    :attribue name: user-friendly name for this converter
    :attribute identifier: unique id for this converter
    :attribute width: output width for this converter, or None to copy the
    input width.  This attribute is set to a default on construction, but can
    be changed to reflect the user overriding the default.
    :attribute height: output height for this converter.  Works just like
    width
    :attribute dont_upsize: should we allow upsizing for conversions? 
    """
    media_type = None
    bitrate = None
    extension = None
    audio_only = False

    def __init__(self, name, width=None, height=None, dont_upsize=True):
        self.name = name
        self.identifier = NON_WORD_CHARS.sub("", name).lower()
        self.width = width
        self.height = height
        self.dont_upsize = dont_upsize

    def get_executable(self):
        raise NotImplementedError

    def get_arguments(self, video, output):
        raise NotImplementedError

    def get_output_filename(self, video):
        basename = os.path.basename(video.filename)
        name, ext = os.path.splitext(basename)
        if ext and ext[0] == '.':
            ext = ext[1:]
        extension = self.extension if self.extension else ext
        return '%s.%s.%s' % (name, self.identifier, extension)

    def get_output_size_guess(self, video):
        if not self.bitrate or not video.duration:
            return None
        if video.duration:
            return self.bitrate * video.duration / 8

    def finalize(self, temp_output, output):
        err = None
        needs_remove = False
        if self.media_type == 'format' and self.extension == 'mp4':
            needs_remove = True
            logging.debug('generic mp4 format detected.  '
                          'Running qtfaststart...')
            try:
                processor.process(temp_output, output)
            except FastStartException:
                logging.exception('qtfaststart: exception occurred')
                err = EnvironmentError('qtfaststart exception')
        else:
            try:
                shutil.move(temp_output, output)
            except EnvironmentError, e:
                needs_remove = True
                err = e
        # If it didn't work for some reason try to clean up the stale stuff.
        # And if that doesn't work ... just log, and re-raise the original
        # error.
        if needs_remove:
            try:
                os.remove(temp_output)
            except EnvironmentError, e:
                logging.error('finalize(): cannot remove stale file %r',
                              temp_output)
                if err:
                    logging.error('finalize(): removal was in response to '
                                  'error: %s', str(err))
                    raise err

    def get_target_size(self, video):
        """Get the size that we will convert to for a given video.

        :returns: (width, height) tuple
        """
	return utils.rescale_video((video.width, video.height),
		(self.width, self.height),
		dont_upsize=self.dont_upsize)

    def process_status_line(self, line):
        raise NotImplementedError

class FFmpegConverterInfo(ConverterInfo):
    """Base class for all ffmpeg-based conversions.

    Subclasses must override the parameters attribute and supply it with the
    ffmpeg command line for the conversion.  parameters can either be a list
    of arguments, or a string in which case split() will be called to create
    the list.
    """
    DURATION_RE = re.compile(r'\W*Duration: (\d\d):(\d\d):(\d\d)\.(\d\d)'
                             '(, start:.*)?(, bitrate:.*)?')
    PROGRESS_RE = re.compile(r'(?:frame=.* fps=.* q=.* )?size=.* time=(.*) '
                             'bitrate=(.*)')
    LAST_PROGRESS_RE = re.compile(r'frame=.* fps=.* q=.* Lsize=.* time=(.*) '
                                  'bitrate=(.*)')

    extension = None
    parameters = None

    def get_executable(self):
        return settings.get_ffmpeg_executable_path()

    def get_arguments(self, video, output):
        args = ['-i', utils.convert_path_for_subprocess(video.filename),
                 '-strict', 'experimental']
        args.extend(settings.customize_ffmpeg_parameters(
            self.get_parameters()))
        if not self.audio_only:
            width, height = self.get_target_size(video)
            args.append("-s")
            args.append('%ix%i' % (width, height))
        args.extend(self.get_extra_arguments(video, output))
        args.append(utils.convert_path_for_subprocess(output))
        return args

    def get_extra_arguments(self, video, output):
        """Subclasses can override this to add argumenst to the ffmpeg command
        line.
        """
        return []

    def get_parameters(self):
        if self.parameters is None:
            raise ValueError("%s: parameters is None" % self)
        elif isinstance(self.parameters, basestring):
            return self.parameters.split()
        else:
            return list(self.parameters)

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

class FFmpegConverterInfo1080p(FFmpegConverterInfo):
    def __init__(self, name):
        FFmpegConverterInfo.__init__(self, name, 1920, 1080)

class FFmpegConverterInfo720p(FFmpegConverterInfo):
    def __init__(self, name):
        FFmpegConverterInfo.__init__(self, name, 1080, 720)

class FFmpegConverterInfo480p(FFmpegConverterInfo):
    def __init__(self, name):
        FFmpegConverterInfo.__init__(self, name, 720, 480)

class ConverterManager(object):
    def __init__(self):
        self.converters = {}
        # converter -> brand reverse map.  XXX: this code, really, really sucks
        # and not very scalable.
        self.brand_rmap = {}
        self.brand_map = {}

    def add_converter(self, converter):
        self.converters[converter.identifier] = converter

    def startup(self):
        self.load_simple_converters()
        self.load_converters(resources.converter_scripts())

    def brand_to_converters(self, brand):
        try:
            return self.brand_map[brand]
        except KeyError:
            return None

    def converter_to_brand(self, converter):
        try:
            return self.brand_rmap[converter]
        except KeyError:
            return None

    def load_simple_converters(self):
        from mvc import basicconverters
        for converter in basicconverters.converters:
            if isinstance(converter, tuple):
                brand, realconverters = converter
                for realconverter in realconverters:
                    self.brand_rmap[realconverter] = brand
                    self.brand_map.setdefault(brand, []).append(realconverter)
                    self.add_converter(realconverter)
            else:
                self.brand_rmap[converter] = None
                self.brand_map.setdefault(None, []).append(converter)
                self.add_converter(converter)

    def load_converters(self, converters):
        for converter_file in converters:
            global_dict = {}
            execfile(converter_file, global_dict)
            if 'converters' in global_dict:
                for converter in global_dict['converters']:
                    if isinstance(converter, tuple):
                        brand, realconverters = converter
                        for realconverter in realconverters:
                            self.brand_rmap[realconverter] = brand
                            self.brand_map.setdefault(brand, []).append(realconverter)
                            self.add_converter(realconverter)
                    else:
                        self.brand_rmap[converter] = None
                        self.brand_map.setdefault(None, []).append(converter)
                        self.add_converter(converter)
                logger.info('load_converters: loaded %i from %r',
                            len(global_dict['converters']),
                            converter_file)

    def list_converters(self):
        return self.converters.values()

    def get_by_id(self, id_):
        return self.converters[id_]

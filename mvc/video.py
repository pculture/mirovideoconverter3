import logging
import re
import subprocess

from mvc.settings import get_ffmpeg_executable_path
from mvc.utils import hms_to_seconds

class VideoFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.container = None
        self.video_codec = None
        self.audio_codec = None
        self.width = None
        self.height = None
        self.duration = None
        self.parse()

    def parse(self):
        self.__dict__.update(
            get_media_info(self.filename))


class Node(object):
    def __init__(self, line="", children=None):
        self.line = line
        if not children:
            self.children = []
        else:
            self.children = children

        if ": " in line:
            self.key, self.value = line.split(": ", 1)
        else:
            self.key = ""
            self.value = ""

    def add_node(self, node):
        self.children.append(node)

    def pformat(self, indent=0):
        s = (" " * indent) + ("Node: %s" % self.line) + "\n"
        for mem in self.children:
            s += mem.pformat(indent + 2)
        return s

    def get_by_key(self, key):
        if self.line.startswith(key):
            return self
        for mem in self.children:
            ret = mem.get_by_key(key)
            if ret:
                return ret
        return None

    def __repr__(self):
        return "<Node %s: %s>" % (self.key, self.value)


def get_indent(line):
    length = len(line)
    line = line.lstrip()
    return (length - len(line), line)


def parse_ffmpeg_output(output):
    """Takes a list of strings and parses it into a loose AST-ish
    thing.

    ffmpeg output uses indentation levels to indicate a hierarchy of
    data.

    If there's a : in the line, then it's probably a key/value pair.

    :param output: the content to parse as a list of strings.

    :returns: a top level node of the ffmpeg output AST
    """
    ast = Node()
    node_stack = [ast]
    indent_level = 0

    for mem in output:
        # skip blank lines
        if len(mem.strip()) == 0:
            continue

        indent, line = get_indent(mem)
        node = Node(line)

        if indent == indent_level:
            node_stack[-1].add_node(node)
        elif indent > indent_level:
            node_stack.append(node_stack[-1].children[-1])
            indent_level = indent
            node_stack[-1].add_node(node)
        else:
            for dedent in range(indent, indent_level, 2):
                # make sure we never pop everything off the stack.
                # the root should always be on the stack.
                if len(node_stack) <= 1:
                    break
                node_stack.pop()
            indent_level = indent
            node_stack[-1].add_node(node)

    return ast


# there's always a space before the size and either a space or a comma
# afterwards.
SIZE_RE = re.compile(" (\\d+)x(\\d+)[ ,]")


def extract_info(ast):
    info = {}
    # logging.info("get_media_info: %s", ast.pformat())

    input0 = ast.get_by_key("Input #0")
    if not input0:
        raise ValueError("no input #0")

    foo, info['container'], bar = input0.line.split(', ', 2)
    if ',' in info['container']:
        info['container'] = info['container'].split(',')

    metadata = input0.get_by_key("Metadata")
    if metadata:
        for key in ('title', 'artist', 'album', 'track', 'genre'):
            node = metadata.get_by_key(key)
            if node:
                info[key] = node.line.split(':', 1)[1].strip()
        major_brand_node = metadata.get_by_key("major_brand")
        extra_container_types = []
        if major_brand_node:
            major_brand = major_brand_node.line.split(':')[1].strip()
            extra_container_types = [major_brand]
        else:
            major_brand = None

        compatible_brands_node = metadata.get_by_key("compatible_brands")
        if compatible_brands_node:
            line = compatible_brands_node.line.split(':')[1].strip()
            extra_container_types.extend(line[i:i+4] for i in range(0, len(line), 4)
                                         if line[i:i+4] != major_brand)

        if extra_container_types:
            if not isinstance(info['container'], list):
                info['container'] = list(info['container'])
            info['container'].extend(extra_container_types)

    duration = input0.get_by_key("Duration:")
    if duration:
        _, rest = duration.line.split(':', 1)
        duration_string, _ = rest.split(', ', 1)
        hours, minutes, seconds = [
            float(i) for i in duration_string.split(':')]
        info['duration'] = hms_to_seconds(hours, minutes, seconds)
        for stream_node in duration.children:
            stream = stream_node.line
            if "Video:" in stream:
                stream_number, video, data = stream.split(': ', 2)
                video_codec = data.split(', ')[0]
                if ' ' in video_codec:
                    video_codec, drmp = video_codec.split(' ', 1)
                    if 'drm' in drmp:
                        info.setdefault('has_drm', []).append('video')
                info['video_codec'] = video_codec
                match = SIZE_RE.search(data)
                if match:
                    info["width"] = int(match.group(1))
                    info["height"] = int(match.group(2))
            elif 'Audio:' in stream:
                stream_number, video, data = stream.split(': ', 2)
                audio_codec = data.split(', ')[0]
                if ' ' in audio_codec:
                    audio_codec, drmp = audio_codec.split(' ', 1)
                    if 'drm' in drmp:
                        info.setdefault('has_drm', []).append('audio')
                info['audio_codec'] = audio_codec
    return info

def get_ffmpeg_output(filepath):

    commandline = [get_ffmpeg_executable_path(),
                   "-i", filepath]
    try:
        output = subprocess.check_output(commandline,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        if e.returncode != 1:
            logging.exception("error calling %r\noutput:%s", commandline,
                              e.output)
        else:
            # ffmpeg -i generally returns 1, so we ignore the exception and
            # just get the output.
            output = e.output

    return output

def get_media_info(filepath):
    """Takes a file path and returns a dict of information about
    this media file that it extracted from ffmpeg -i.

    :param filepath: absolute path to the media file in question

    :returns: dict of media info possibly containing: height, width,
    container, audio_codec, video_codec
    """
    output = get_ffmpeg_output(filepath)
    ast = parse_ffmpeg_output(output.splitlines())

    return extract_info(ast)

import sys
from setuptools import setup

if sys.version < '2.7':
    raise RuntimeError('MVC requires Python 2.7')

setup(
    name='Miro Video Converter',
    description='Simple Video Converter',
    author='Participatory Culture Foundation',
    author_email='ben@pculture.org',
    url='http://www.mirovideoconverter.com/',
    license='GPL',
    version=3.0,
    packages=[
        'mvc',
        'mvc.resources',
        'mvc.widgets',
        'mvc.widgets.gtk',
        'mvc.ui',
        'mvc.qtfaststart',
    ],
    package_data={
        'mvc.resources': [
            'converters/*.py',
            'images/*.*',
        ],
    },
    scripts=['scripts/miro-video-converter.py'],
)

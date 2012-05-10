Miro Video Converter 3
======================

<img src="http://cl.ly/ECBE/o"/></img>

MVC3 has a complete UI overhaul designed to maintain the simplicity of previous versions but also provide
users with batch processing options and give users greater control over their converted files.


This directory holds the UI tests for mvc that can be run like this:

1. install Sikuli from http://sikuli.org
2. install nose (pip install nose)
3. set 2 environment variables:
 - export SIKULI_HOME = *path to sikuli-script.jar*
 - export PYTHON_PKGS = *path to where nose packages live* (because jython is annoying and it's the only way I can get it to import)

i4. cd ../ (on dir level above the tests.sikuli directory
5. java -jar $SIKULI_HOME/sikuli-script.jar uitests.sikuli








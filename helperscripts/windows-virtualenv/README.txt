Helper script to create a windows virtual environment.

Dependencies:
  - cygwin
  - 7zip

Instructions:
  Run python <path to window-virtualenv-dir> <env-directory>

  After this <env-directory> will be a virtualenv directory that has pygtk and
  ffmpeg loaded into it.

  Run:

  source <env-directory>/Scripts/activate

  To set your PATH and other env variables to use that virtualenv.

Warning: using the ~ char didn't seem to work for me under cygwin


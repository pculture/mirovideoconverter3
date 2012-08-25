# before anything else, settup logging
from mvc.windows import exelogging
exelogging.setup_logging()

import os
import sys

from mvc import settings
from mvc.ui.widgets import Application

# add the directories for ffmpeg and avconv to our search path
exe_dir = os.path.dirname(sys.executable)
settings.add_to_search_path(os.path.join(exe_dir, 'ffmpeg'))
settings.add_to_search_path(os.path.join(exe_dir, 'avconv'))
# run the app
app = Application()
app.startup()
app.run()

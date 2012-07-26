from mvc.windows import exelogging
exelogging.setup_logging()

from mvc.ui.widgets import Application
app = Application()
app.startup()
app.run()

import os
import sys

from mvc.osx import autoupdate
from mvc.widgets import app
from mvc.widgets import initialize
from mvc.ui.widgets import Application

# run the app
autoupdate.initialize()
app.widgetapp = Application()
initialize(app.widgetapp)

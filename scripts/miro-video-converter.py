#!/usr/bin/python

try:
    from mvc.ui.widgets import Application
except ImportError:
    from mvc.ui.console import Application
from mvc.widgets import app
from mvc.widgets import initialize
app.widgetapp = Application()
initialize(app.widgetapp)

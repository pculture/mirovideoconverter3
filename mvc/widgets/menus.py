# menus.py
#
# Most of these are taken from libs/frontends/widgets/menus.py in the miro
# project.
#
# TODO: merge common bits!

import collections

from mvc.widgets import signals
from mvc.widgets import widgetutil
from mvc.widgets import widgetset
from mvc.widgets import app

from mvc.widgets.keyboard import (Shortcut, CTRL, ALT, SHIFT, CMD,
     MOD, RIGHT_ARROW, LEFT_ARROW, UP_ARROW, DOWN_ARROW, SPACE, ENTER, DELETE,
     BKSPACE, ESCAPE, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12)

# XXX hack:

def _(text, *params):
    if params:
       return text % params[0]
    return text

class MenuItem(widgetset.MenuItem):
    """Portable MenuItem class.

    This adds group handling to the platform menu items.
    """
    # group_map is used for the legacy menu updater code
    group_map = collections.defaultdict(set)

    def __init__(self, label, name, shortcut=None, groups=None,
                 **state_labels):
        widgetset.MenuItem.__init__(self, label, name, shortcut)
        # state_labels is used for the legacy menu updater code
        self.state_labels = state_labels
        if groups:
            if len(groups) > 1:
                raise ValueError("only support one group")
            MenuItem.group_map[groups[0]].add(self)

class MenuItemFetcher(object):
    """Get MenuItems by their name quickly.  """

    def __init__(self):
        self._cache = {}

    def __getitem__(self, name):
        if name in self._cache:
            return self._cache[name]
        else:
            menu_item = app.widgetapp.menubar.find(name)
            self._cache[name] = menu_item
            return menu_item

def get_app_menu():
    """Returns the default menu structure."""

    app_name = "Miro Video Converter"    # XXX HACK

    file_menu = widgetset.Menu(_("_File"), "FileMenu", [
                    MenuItem(_("_Open"), "Open", Shortcut("o", MOD),
                             groups=["NonPlaying"]),
                    MenuItem(_("_Quit"), "Quit", Shortcut("q", MOD)),
                    ])
    help_menu = widgetset.Menu(_("_Help"), "HelpMenu", [
                    MenuItem(_("About %(name)s",
                               {'name': app_name}),
                             "About")
                    ])

    all_menus = [file_menu, help_menu]
    return all_menus

action_handlers = {}
group_action_handlers = {}

def on_menubar_activate(menubar, action_name):
    callback = lookup_handler(action_name)
    if callback is not None:
        callback()

def lookup_handler(action_name):
    """For a given action name, get a callback to handle it.  Return
    None if no callback is found.
    """
   
    retval = _lookup_group_handler(action_name)
    if retval is None:
        retval = action_handlers.get(action_name)
    return retval

def _lookup_group_handler(action_name):
    try:
        group_name, callback_arg = action_name.split('-', 1)
    except ValueError:
        return None # split return tuple of length 1
    try:
        group_handler = group_action_handlers[group_name]
    except KeyError:
        return None
    else:
        return lambda: group_handler(callback_arg)

def action_handler(name):
    """Decorator for functions that handle menu actions."""
    def decorator(func):
        action_handlers[name] = func
        return func
    return decorator

def group_action_handler(action_prefix):
    def decorator(func):
        group_action_handlers[action_prefix] = func
        return func
    return decorator

# File menu
@action_handler("Open")
def on_open():
    app.widgetapp.choose_file()

@action_handler("Quit")
def on_quit():
    app.widgetapp.quit()

# Help menu
@action_handler("About")
def on_about():
    app.widgetapp.about()

class MenuManager(signals.SignalEmitter):
    """Updates the menu based on the current selection.

    This includes enabling/disabling menu items, changing menu text
    for plural selection and enabling/disabling the play button.  The
    play button is obviously not a menu item, but it's pretty closely
    related

    Whenever code makes a change that could possibly affect which menu
    items should be enabled/disabled, it should call the
    update_menus() method.

    Signals:
    - menus-updated(reasons): Emitted whenever update_menus() is called
    """
    def __init__(self):
        signals.SignalEmitter.__init__(self, 'menus-updated')
        self.menu_item_fetcher = MenuItemFetcher()
        #self.subtitle_encoding_updater = SubtitleEncodingMenuUpdater()
        self.subtitle_encoding_updater = None

    def setup_menubar(self, menubar):
        """Setup the main miro menubar.
        """
        menubar.add_initial_menus(get_app_menu())
        menubar.connect("activate", on_menubar_activate)
        self.menu_updaters = []

    def _set_play_pause(self):
        if ((not app.playback_manager.is_playing
             or app.playback_manager.is_paused)):
            label = _('Play')
        else:
            label = _('Pause')
        self.menu_item_fetcher['PlayPauseItem'].set_label(label)

    def add_subtitle_encoding_menu(self, category_label, *encodings):
        """Set up a subtitles encoding menu.

        This method should be called for each category of subtitle encodings
        (East Asian, Western European, Unicode, etc).  Pass it the list of
        encodings for that category.

        :param category_label: human-readable name for the category
        :param encodings: list of (label, encoding) tuples.  label is a
            human-readable name, and encoding is a value that we can pass to
            VideoDisplay.select_subtitle_encoding()
        """
        self.subtitle_encoding_updater.add_menu(category_label, encodings)

    def select_subtitle_encoding(self, encoding):
        if not self.subtitle_encoding_updater.has_encodings():
            # OSX never sets up the subtitle encoding menu
            return
        menu_item_name = self.subtitle_encoding_updater.action_name(encoding)
        try:
            self.menu_item_fetcher[menu_item_name].set_state(True)
        except KeyError:
            logging.warn("Error enabling subtitle encoding menu item: %s",
                         menu_item_name)

    def update_menus(self, *reasons):
        """Call this when a change is made that could change the menus

        Use reasons to describe why the menus could change.  Some MenuUpdater
        objects will do some optimizations based on that
        """
        reasons = set(reasons)
        self._set_play_pause()
        for menu_updater in self.menu_updaters:
            menu_updater.update(reasons)
        self.emit('menus-updated', reasons)

class MenuUpdater(object):
    """Base class for objects that dynamically update menus."""
    def __init__(self, menu_name):
        self.menu_name = menu_name
        self.first_update = False

    # we lazily access our menu item, since we are created before the menubar
    # is fully setup.
    def get_menu(self):
        try:
            return self._menu
        except AttributeError:
            self._menu = app.widgetapp.menubar.find(self.menu_name)
            return self._menu
    menu = property(get_menu)

    def update(self, reasons):
        if not self.first_update and not self.should_process_update(reasons):
            return
        self.first_update = False
        self.start_update()
        if not self.should_show_menu():
            self.menu.hide()
            return

        self.menu.show()
        if self.should_rebuild_menu():
            self.clear_menu()
            self.populate_menu()
        self.update_items()

    def should_process_update(self, reasons):
        """Test if we should ignore the update call.

        :param reasons: the reasons passed in to MenuManager.update_menus()
        """
        return True

    def clear_menu(self):
        """Remove items from our menu before rebuilding it."""
        for child in self.menu.get_children():
            self.menu.remove(child)

    def start_update(self):
        """Called at the very start of the update method.  """
        pass

    def should_show_menu(self):
        """Should we display the menu?  """
        return True

    def should_rebuild_menu(self):
        """Should we rebuild the menu structure?"""
        return False

    def populate_menu(self):
        """Add MenuItems to our menu."""
        pass

    def update_items(self):
        """Update our menu items."""
        pass

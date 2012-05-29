import gtk
import gobject

from .image import Image
from .layoutmanager import LayoutManager

TYPE_MAPPING = {
    str: gobject.TYPE_STRING,
    unicode: gobject.TYPE_STRING,
    int: gobject.TYPE_INT,
    float: gobject.TYPE_FLOAT,
    Image: gobject.TYPE_OBJECT
    }

class TableModel(gtk.ListStore):

    def __init__(self, column_types):
        super(TableModel, self).__init__(*[TYPE_MAPPING[t] for t in column_types])

    def update_iter(self, iter_, values):
        [self.set_value(iter_, i, v)
         for i, v in enumerate(values)]


class TableColumn(object):
    """A single column of a TableView.

    Signals:

        clicked (table_column) -- The header for this column was clicked.
    """
    # GTK hard-codes 4px of padding for each column
    FIXED_PADDING = 4
    def __init__(self, title, renderer, header=None, **attrs):
        # header widget not used yet in GTK (#15800)
        self._column = gtk.TreeViewColumn(title, renderer._renderer)
        self._column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.attrs = attrs
        renderer.setup_attributes(self._column, attrs)
        self.renderer = renderer
        self.do_horizontal_padding = True

    def set_right_aligned(self, right_aligned):
        """Horizontal alignment of the header label."""
        if right_aligned:
            self._column.set_alignment(1.0)
        else:
            self._column.set_alignment(0.0)

    def set_min_width(self, width):
        self._column.props.min_width = width + TableColumn.FIXED_PADDING

    def set_max_width(self, width):
        self._column.props.max_width = width

    def set_width(self, width):
        self._column.set_fixed_width(width + TableColumn.FIXED_PADDING)

    def get_width(self):
        return self._column.get_width()

    def set_resizable(self, resizable):
        """Set if the user can resize the column."""
        self._column.set_resizable(resizable)

    def set_do_horizontal_padding(self, horizontal_padding):
        self.do_horizontal_padding = False

    def set_sort_indicator_visible(self, visible):
        """Show/Hide the sort indicator for this column."""
        self._column.set_sort_indicator(visible)

    def get_sort_indicator_visible(self):
        return self._column.get_sort_indicator()

    def set_sort_order(self, ascending):
        """Display a sort indicator on the column header.  Ascending can be
        either True or False which affects the direction of the indicator.
        """
        if ascending:
            self._column.set_sort_order(gtk.SORT_ASCENDING)
        else:
            self._column.set_sort_order(gtk.SORT_DESCENDING)

    def get_sort_order_ascending(self):
        """Returns if the sort indicator is displaying that the sort is
        ascending.
        """
        return self._column.get_sort_order() == gtk.SORT_ASCENDING


class TableView(gtk.TreeView):

    def __init__(self, model):
        super(TableView, self).__init__(model)
        self.layout_manager = LayoutManager(self)
        self.set_size_request(-1, 200)

    def add_column(self, column):
        self.append_column(column._column)



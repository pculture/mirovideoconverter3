import gtk
import gobject

TABLE_COLUMNS = (
    ("Name", gobject.TYPE_STRING),
    ("Output", gobject.TYPE_STRING),
    ("Converter", gobject.TYPE_STRING),
    ("Status", gobject.TYPE_STRING),
    ("Duration", gobject.TYPE_INT),
    ("Progress", gobject.TYPE_INT),
    ("ETA", gobject.TYPE_INT))

TYPE_MAPPING = {
    str: gobject.TYPE_STRING,
    unicode: gobject.TYPE_STRING,
    int: gobject.TYPE_INT
    }

class TableModel(gtk.ListStore):

    def __init__(self, column_types):
        super(TableModel, self).__init__(*[TYPE_MAPPING[t] for t in column_types])

    def update_iter(self, iter_, values):
        [self.set_value(iter_, i, v)
         for i, v in enumerate(values)]


class TableView(gtk.TreeView):

    def __init__(self, model):
        super(TableView, self).__init__(model)
        self.set_size_request(-1, 200)

    def add_column(self, name):
        i = len(self.get_columns())
        self.insert_column_with_attributes(i, name, gtk.CellRendererText(),
                                           text=i)


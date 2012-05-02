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


class ConversionModel(gtk.ListStore):

    def __init__(self):
        super(ConversionModel, self).__init__(*[c[1] for c in TABLE_COLUMNS])


class ConversionTable(gtk.TreeView):

    def __init__(self):
        model = ConversionModel()
        super(ConversionTable, self).__init__(model)
        self.set_size_request(-1, 200)
        for i, (name, type_) in enumerate(TABLE_COLUMNS):
            self.insert_column_with_attributes(
                i, name, gtk.CellRendererText(), text=i)
        self._conversion_to_iter = {}

    def update_conversion(self, conversion):
        values = (conversion.video.filename,
                  conversion.output,
                  conversion.converter.name,
                  conversion.status,
                  conversion.duration or 0,
                  conversion.progress or 0,
                  conversion.eta or 0)
        model = self.get_model()
        if conversion not in self._conversion_to_iter:
            iter_ = model.append(values)
            self._conversion_to_iter[conversion] = iter_
        else:
            iter_ = self._conversion_to_iter[conversion]
            [model.set_value(iter_, i, v)
             for i, v in enumerate(values)]


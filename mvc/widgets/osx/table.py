import math

from AppKit import *

from .base import Widget

def calc_row_height(view, model_row):
    max_height = 0
    model = view.dataSource().model
    try:
        row = model[model_row]
    except IndexError:
        pass
    else:
        for column in view.tableColumns():
            cell = column.dataCell()
            data = row[int(column.identifier())]
            cell.setObjectValue_(data)
            font = cell.font()
            cell_height = math.ceil(font.ascender() + abs(font.descender()) +
                                    font.leading())
            max_height = max(max_height, cell_height)
    if max_height == 0:
        max_height = 12
    return max_height

class TableModel(object):
    def __init__(self, column_types):
        self.column_types = column_types
        self.rows = []
        self.callbacks = set()

    def add_change_callback(self, callback):
        self.callbacks.add(callback)

    def changed(self):
        for callback in self.callbacks:
            callback()

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        return self.rows[index]

    def check_values(self, values):
        if len(values) != len(self.column_types):
            raise ValueError("tried to append the wrong # of columns")

    def append(self, values):
        self.check_values(values)
        retval = len(self.rows)
        self.rows.append([str(v) for v in values])
        self.changed()
        return retval # the index of the new values

    def update_iter(self, iter_, values):
        self.check_values(values)
        self.rows[iter_] = [str(v) for v in values]
        self.changed()


class TableDataSource(NSObject, protocols.NSTableViewDataSource):
    def initWithModel_(self, model):
        self = self.init()
        self.model = model
        return self

    def numberOfRowsInTableView_(self, table_view):
        return len(self.model)

    def tableView_objectValueForTableColumn_row_(self, table_view,
                                                 column, row):
        id_ = int(column.identifier())
        return self.model[row][id_]


class TableView(Widget):
    CREATES_VIEW = False

    def __init__(self, model):
        self.model = model
        self.model.add_change_callback(self.model_changed)
        self.view = NSTableView.alloc().init()
        self.data_source = TableDataSource.alloc().initWithModel_(model)
        self.view.setRowHeight_(12)
        self.row_height_set = False
        self.view.setDataSource_(self.data_source)
        self.view.reloadData()
        self.header_view = NSTableHeaderView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 200, 17))
        self.view.setHeaderView_(self.header_view)
        super(TableView, self).__init__()

    def calc_size_request(self):
        self.view.tile()
        frame = self.view.frame()
        return frame.size.width, frame.size.height + 17 + 20

    def model_changed(self):
        if not self.row_height_set:
            self.try_to_set_row_height()
        self.invalidate_size_request()
        self.view.reloadData()

    def add_column(self, name):
        id_ = len(self.view.tableColumns())
        column = NSTableColumn.alloc().initWithIdentifier_(str(id_))
        header_cell = NSTableHeaderCell.alloc().init()
        header_cell.setStringValue_(name)
        column.setHeaderCell_(header_cell)
        self.view.addTableColumn_(column)
        if not self.row_height_set:
            self.try_to_set_row_height()

    def try_to_set_row_height(self):
        if len(self.model):
            self.view.setRowHeight_(calc_row_height(self.view, 0))
            self.row_height_set = True

    def viewport_created(self):
        self.viewport.view.addSubview_(self.header_view)
        self.viewport.view.addSubview_(self.view)
        self._do_layout()

    def viewport_repositioned(self):
        self._do_layout()

    def _do_layout(self):
        x = self.viewport.placement.origin.x
        y = self.viewport.placement.origin.y
        width = self.viewport.get_width()
        height = self.viewport.get_height()
        self.header_view.setFrame_(NSMakeRect(x, y, width, 17))
        self.view.setFrame_(NSMakeRect(x, y + 17, width, height - 17))
        self.viewport.queue_redraw()

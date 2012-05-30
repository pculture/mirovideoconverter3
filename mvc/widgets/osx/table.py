import math

from AppKit import *

from .base import Widget
from .drawing import DrawingStyle, DrawingContext
from .layoutmanager import LayoutManager

def calc_row_height(view, model_row):
    max_height = 0
    model = view.dataSource().model
    for column in view.tableColumns():
        cell = column.dataCell()
        data = model.get_column_data(model_row, column)
        cell.setObjectValue_(data)
        cell_height = cell.calcHeight_(view)
        max_height = max(max_height, cell_height)
    if max_height == 0:
        max_height = 12
    return max_height


def _calc_interior_frame(total_frame, tableview):
    """Calculate the inner cell area for a table cell.

    We tell cocoa that the intercell spacing is (0, 0) and instead handle the
    spacing ourselves.  This method calculates the area that a cell should
    render to, given the total spacing.
    """
    return NSMakeRect(total_frame.origin.x + 1,
            total_frame.origin.y + 1,
            total_frame.size.width - 1,
            total_frame.size.height - 1)


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

    def get_column_data(self, row, column):
        attr_map = column.identifier()
        row = self[row]
        return dict((name, row[index])
                    for name, index in attr_map.items())

    def append(self, values):
        self.check_values(values)
        retval = len(self.rows)
        self.rows.append(values)
        self.changed()
        return retval # the index of the new values

    def update_iter(self, iter_, values):
        self.check_values(values)
        self.rows[iter_] = values
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
        return self.model.get_column_data(row, column)


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
        super(TableView, self).__init__()

    def calc_size_request(self):
        self.view.tile()
        frame = self.view.frame()
        return frame.size.width, frame.size.height + 17 + 20

    def model_changed(self):
        if not self.row_height_set:
            self.try_to_set_row_height()
        self.view.reloadData()
        self.invalidate_size_request()

    def add_column(self, column):
        id_ = len(self.view.tableColumns())
        column.set_index(id_)
        self.view.addTableColumn_(column._column)
        self._set_min_max_column_widths(column)
        self.view.noteNumberOfRowsChanged()
        self.invalidate_size_request()
        if not self.row_height_set:
            self.try_to_set_row_height()

    def _set_min_max_column_widths(self, column):
        spacing = 3
        if column.min_width > 0:
            column._column.setMinWidth_(column.min_width + spacing)
        if column.max_width > 0:
            column._column.setMaxWidth_(column.max_width + spacing)

    def try_to_set_row_height(self):
        if len(self.model):
            self.view.setRowHeight_(calc_row_height(self.view, 0))
            self.row_height_set = True

    def viewport_created(self):
        self.viewport.view.addSubview_(self.view)
        self._do_layout()

    def viewport_repositioned(self):
        self._do_layout()

    def _do_layout(self):
        x = self.viewport.placement.origin.x
        y = self.viewport.placement.origin.y
        width = self.viewport.get_width()
        height = self.viewport.get_height()
        self.view.setFrame_(NSMakeRect(x, y, width, height))
        self.viewport.queue_redraw()


class TableColumn(object):
    def __init__(self, title, renderer, header=None, **attrs):
        self._column = NSTableColumn.alloc().initWithIdentifier_(attrs)
        self._column.setEditable_(NO)
        self._column.setResizingMask_(NSTableColumnNoResizing)
        self.renderer = renderer
        self.sort_order_ascending = True
        self.sort_indicator_visible = False
        self.do_horizontal_padding = True
        self.min_width = self.max_width = None
        renderer.setDataCell_(self._column)

    def set_do_horizontal_padding(self, horizontal_padding):
        self.do_horizontal_padding = horizontal_padding

    def set_min_width(self, width):
        self.min_width = width

    def set_max_width(self, width):
        self.max_width = width

    def set_width(self, width):
        self._column.setWidth_(width)

    def get_width(self):
        return self._column.width()

    def set_resizable(self, resizable):
        mask = 0
        if resizable:
            mask |= NSTableColumnUserResizingMask
        self._column.setResizingMask_(mask)

    def set_index(self, index):
        self.index = index
        self.renderer.set_index(index)


class MVCTableCell(NSTextFieldCell):
    def init(self):
        return super(MVCTableCell, self).initTextCell_('')

    def calcHeight_(self, view):
        font = self.font()
        return math.ceil(font.ascender() + abs(font.descender()) +
                font.leading())

    def highlightColorWithFrame_inView_(self, frame, view):
        return nil

    def setObjectValue_(self, value_dict):
        if isinstance(value_dict, dict):
            NSCell.setObjectValue_(self, value_dict['value'])
        else:
            # OS X calls setObjectValue_('') on intialization
            NSCell.setObjectValue_(self, value_dict)

    def drawInteriorWithFrame_inView_(self, frame, view):
        return NSTextFieldCell.drawInteriorWithFrame_inView_(self,
                _calc_interior_frame(frame, view), view)


class MVCTableImageCell(NSImageCell):
    def calcHeight_(self, view):
        return self.value_dict['image'].size().height

    def highlightColorWithFrame_inView_(self, frame, view):
        return nil

    def setObjectValue_(self, value_dict):
        NSImageCell.setObjectValue_(self, value_dict['image'])

    def drawInteriorWithFrame_inView_(self, frame, view):
        return NSImageCell.drawInteriorWithFrame_inView_(self,
                _calc_interior_frame(frame, view), view)


class CellRendererBase(object):
    DRAW_BACKGROUND = True

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index


class CellRenderer(CellRendererBase):
    def __init__(self):
        self.cell = self.build_cell()
        self._font_scale_factor = 1.0
        self._font_bold = False
        self.set_align('left')

    def build_cell(self):
        return MVCTableCell.alloc().init()

    def setDataCell_(self, column):
        column.setDataCell_(self.cell)

    def set_text_size(self, size):
        if size == widgetconst.SIZE_NORMAL:
            self._font_scale_factor = 1.0
        elif size == widgetconst.SIZE_SMALL:
            # make the scale factor such so that the font size is 11.0
            self._font_scale_factor = 11.0 / NSFont.systemFontSize()
        else:
            raise ValueError("Unknown size: %s" % size)
        self._set_font()

    def set_font_scale(self, scale_factor):
        self._font_scale_factor = scale_factor
        self._set_font()

    def set_bold(self, bold):
        self._font_bold = bold
        self._set_font()

    def _set_font(self):
        size = NSFont.systemFontSize() * self._font_scale_factor
        if self._font_bold:
            font = NSFont.boldSystemFontOfSize_(size)
        else:
            font = NSFont.systemFontOfSize_(size)
        self.cell.setFont_(font)

    def set_color(self, color):
        color = NSColor.colorWithDeviceRed_green_blue_alpha_(color[0],
                color[1], color[2], 1.0)
        self.cell._textColor = color
        self.cell.setTextColor_(color)

    def set_align(self, align):
        if align == 'left':
            ns_alignment = NSLeftTextAlignment
        elif align == 'center':
            ns_alignment = NSCenterTextAlignment
        elif align == 'right':
            ns_alignment = NSRightTextAlignment
        else:
            raise ValueError("unknown alignment: %s", align)
        self.cell.setAlignment_(ns_alignment)


class ImageCellRenderer(CellRendererBase):
    def setDataCell_(self, column):
        column.setDataCell_(MVCTableImageCell.alloc().init())


class CustomTableCell(NSCell):
    def init(self):
        self = super(CustomTableCell, self).init()
        self.layout_manager = LayoutManager()
        self.hotspot = None
        self.default_drawing_style = DrawingStyle()
        return self

    def highlightColorWithFrame_inView_(self, frame, view):
        return nil

    def calcHeight_(self, view):
        self.layout_manager.reset()
        self.set_wrapper_data()
        cell_size = self.wrapper.get_size(self.default_drawing_style,
                self.layout_manager)
        return cell_size[1]

    def make_drawing_style(self, frame, view):
        text_color = None
        if (self.isHighlighted() and frame is not None and
                (view.isDescendantOf_(view.window().firstResponder()) or
                    view.gradientHighlight) and view.window().isMainWindow()):
            text_color = NSColor.whiteColor()
        return DrawingStyle(text_color=text_color)

    def drawInteriorWithFrame_inView_(self, frame, view):
        NSGraphicsContext.currentContext().saveGraphicsState()
        if not self.wrapper.IGNORE_PADDING:
            # adjust frame based on the cell spacing. We also have to adjust
            # the hover position to account for the new frame
            original_frame = frame
            frame = _calc_interior_frame(frame, view)
            hover_adjustment = (frame.origin.x - original_frame.origin.x,
                                frame.origin.y - original_frame.origin.y)
        else:
            hover_adjustment = (0, 0)
        if self.wrapper.outline_column:
            pad_left = EXPANDER_PADDING
        else:
            pad_left = 0
        drawing_rect = NSMakeRect(frame.origin.x + pad_left, frame.origin.y,
                frame.size.width - pad_left, frame.size.height)
        context = DrawingContext(view, drawing_rect, drawing_rect)
        context.style = self.make_drawing_style(frame, view)
        self.layout_manager.reset()
        self.set_wrapper_data()
        column = self.wrapper.get_index()
        # hover_pos = view.get_hover(self.row, column)
        # if hover_pos is not None:
        #     hover_pos = [hover_pos[0] - hover_adjustment[0],
        #                  hover_pos[1] - hover_adjustment[1]]
        hover_pos = None
        self.wrapper.render(context, self.layout_manager, self.isHighlighted(),
                self.hotspot, hover_pos)
        NSGraphicsContext.currentContext().restoreGraphicsState()

    def setObjectValue_(self, value):
        self.object_value = value

    def set_wrapper_data(self):
        self.wrapper.__dict__.update(self.object_value)


class CustomCellRenderer(CellRendererBase):
    CellClass = CustomTableCell

    IGNORE_PADDING = False

    def __init__(self):
        self.outline_column = False
        self.index = None

    def setDataCell_(self, column):
        # Note that the ownership is the opposite of what happens in widgets.
        # The NSObject owns it's wrapper widget.  This happens for a couple
        # reasons:
        # 1) The data cell gets copied a bunch of times, so wrappermap won't
        # work with it.
        # 2) The Wrapper should only needs to stay around as long as the
        # NSCell that it's wrapping is around.  Once the column gets removed
        # from the table, the wrapper can be deleted.
        nscell = self.CellClass.alloc().init()
        nscell.wrapper = self
        column.setDataCell_(nscell)

    def hotspot_test(self, style, layout, x, y, width, height):
        return None

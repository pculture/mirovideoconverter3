from mvc.widgets import *

def align(widget, xalign=0, yalign=0, xscale=0, yscale=0,
        top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Create an alignment, then add widget to it and return the alignment.
    """
    alignment = Alignment(xalign, yalign, xscale, yscale,
                          top_pad, bottom_pad, left_pad, right_pad)
    alignment.add(widget)
    return alignment

def align_center(widget, top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Wrap a widget in an Alignment that will center it horizontally.
    """
    return align(widget, 0.5, 0, 0, 1,
            top_pad, bottom_pad, left_pad, right_pad)

def align_right(widget, top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Wrap a widget in an Alignment that will align it left.
    """
    return align(widget, 1, 0, 0, 1, top_pad, bottom_pad, left_pad, right_pad)

def align_left(widget, top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Wrap a widget in an Alignment that will align it right.
    """
    return align(widget, 0, 0, 0, 1, top_pad, bottom_pad, left_pad, right_pad)

def align_middle(widget, top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Wrap a widget in an Alignment that will center it vertically.
    """
    return align(widget, 0, 0.5, 1, 0,
            top_pad, bottom_pad, left_pad, right_pad)

def align_top(widget, top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Wrap a widget in an Alignment that will align to the top.
    """
    return align(widget, 0, 0, 1, 0, top_pad, bottom_pad, left_pad, right_pad)

def align_bottom(widget, top_pad=0, bottom_pad=0, left_pad=0, right_pad=0):
    """Wrap a widget in an Alignment that will align to the bottom.
    """
    return align(widget, 0, 1, 1, 0, top_pad, bottom_pad, left_pad, right_pad)

def pad(widget, top=0, bottom=0, left=0, right=0):
    """Wrap a widget in an Alignment that will pad it.
    """
    alignment = Alignment(0, 0, 1, 1,
                          top, bottom, left, right)
    alignment.add(widget)
    return alignment


import logging

class WidgetMixin(object):
    def __init__(self):
        super(WidgetMixin, self).__init__()
        self._new_signals = {}

    def create_signal(self, signal_name):
        if signal_name in self._new_signals:
            raise RuntimeError('tried to recreate signal %r' % signal_name)
        self._new_signals[signal_name] = set()

    def connect(self, signal_name, handler, *args):
        if signal_name in self._new_signals:
            self._new_signals[signal_name].add((handler, args))
        else:
            super(WidgetMixin, self).connect(signal_name, handler, *args)

    def emit(self, signal_name, *signal_args):
        if signal_name in self._new_signals:
            for handler, args in self._new_signals[signal_name]:
                try:
                    handler(self, *(signal_args + args))
                except:
                    logging.exception('while handling signal %r (%r) on %r',
                                      signal_name, args, self)
        else:
            super(WidgetMixin, self).emit(signal_name, *args)


class BinMixin(WidgetMixin):
    def add(self, widget):
        widget.show()
        super(BinMixin, self).add(widget)

    def set_child(self, widget):
        old_child = self.get_child()
        if old_child is not None:
            self.remove(old_child)
        self.add(widget)

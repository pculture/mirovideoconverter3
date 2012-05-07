import logging
import traceback

from Foundation import *
from objc import nil

class NotificationForwarder(NSObject):
    """Forward notifications from a Cocoa object to a python class.  
    """

    def initWithNSObject_center_(self, nsobject, center):
        """Initialize the NotificationForwarder nsobject is the NSObject to
        forward notifications for.  It can be nil in which case notifications
        from all objects will be forwarded.

        center is the NSNotificationCenter to get notifications from.  It can
        be None, in which cas the default notification center is used.
        """
        self.nsobject = nsobject
        self.callback_map = {}
        if center is None:
            self.center = NSNotificationCenter.defaultCenter()
        else:
            self.center = center
        return self

    @classmethod
    def create(cls, object, center=None):
        """Helper method to call aloc() then initWithNSObject_center_()."""
        return cls.alloc().initWithNSObject_center_(object, center)

    def connect(self, callback, name):
        """Register to listen for notifications.
        Only one callback for each notification name can be connected.
        """

        if name in self.callback_map:
            raise ValueError("%s already connected" % name)

        self.callback_map[name] = callback
        self.center.addObserver_selector_name_object_(self, 'observe:', name,
                self.nsobject)

    def disconnect(self, name=None):
        if name is not None:
            self.center.removeObserver_name_object_(self, name, self.nsobject)
            self.callback_map.pop(name)
        else:
            self.center.removeObserver_(self)
            self.callback_map.clear()

    def observe_(self, notification):
        name = notification.name()
        callback = self.callback_map[name]
        if callback is None:
            logging.warn("Callback for %s is dead", name)
            self.center.removeObverser_name_object_(self, name, self.nsobject)
            return
        try:
            callback(notification)
        except:
            logging.warn("Callback for %s raised exception:%s\n", name,
                    traceback.format_exc())

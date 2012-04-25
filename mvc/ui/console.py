import time
import mvc

class Application(mvc.Application):

    def run(self):
        import sys
        filename, converter_id = sys.argv[1:3]
        c = app.start_conversion(filename, converter_id)
        print 'Converting', filename, 'to', c.output
        def changed(c):
            print 'Status', c.__dict__
        c.listen(changed)

        # XXX real mainloop
        while self.conversion_manager.running:
            self.conversion_manager.check_notifications()
            time.sleep(1)

if __name__ == "__main__":
    app = Application()
    app.startup()
    app.run()

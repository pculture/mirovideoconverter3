import operator
import optparse
import time
import sys

import mvc

parser = optparse.OptionParser(
    usage='%prog [-l] [--list-converters] [-c <converter> <filenames..>]',
    version='%prog ' + mvc.VERSION,
    prog='python -m mvc.ui.console')
parser.add_option('-l', '--list-converters', action='store_true',
                  dest='list_converters',
                  help="Print a list of supported converter types.")
parser.add_option('-c', '--converter', dest='converter',
                  help="Specify the type of conversion to make.")

class Application(mvc.Application):

    def run(self):
        (options, args) = parser.parse_args()

        if options.list_converters:
            for c in sorted(self.converter_manager.list_converters(),
                            key=operator.attrgetter('name')):
                print '%s (-c %s)' % (
                    c.name,
                    c.identifier)
            return

        try:
            self.converter_manager.get_by_id(options.converter)
        except KeyError:
            print 'ERROR: %r is not a valid converter type.' % (
                options.converter,)
            print 'Use "%s -l" to get a list of valid converters.' % (
                parser.prog,)
            print
            parser.print_help()
            sys.exit(1)

        for filename in args:
            def changed(c):
                if c.status == 'initialized':
                    line = 'starting (output: %s)' % (c.output,)
                elif c.status == 'converting':
                    if c.progress_percent is not None:
                        line = 'converting (%i%% complete, %is remaining)' % (
                            c.progress_percent * 100, c.eta)
                    else:
                        line = 'converting (0% complete, unknown remaining)'
                elif c.status == 'staging':
                    line = 'staging'
                elif c.status == 'failed':
                    line = 'failed (error: %r)' % (c.error,)
                elif c.status == 'finished':
                    line = 'finished (output: %s)' % (c.output,)
                else:
                    line = c.status
                print '%s: %s' % (c.video.filename, line)
            c = app.start_conversion(filename, options.converter)
            changed(c)
            c.listen(changed)

        # XXX real mainloop
        while self.conversion_manager.running:
            self.conversion_manager.check_notifications()
            time.sleep(1)
        self.conversion_manager.check_notifications() # one last time

if __name__ == "__main__":
    app = Application()
    app.startup()
    app.run()

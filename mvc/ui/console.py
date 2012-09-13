import json
import operator
import optparse
import time
import sys

import mvc
from mvc.widgets import app
from mvc.widgets import initialize

parser = optparse.OptionParser(
    usage='%prog [-l] [--list-converters] [-c <converter> <filenames..>]',
    version='%prog ' + mvc.VERSION,
    prog='python -m mvc.ui.console')
parser.add_option('-j', '--json', action='store_true',
                  dest='json',
                  help='Output JSON documents, rather than text.')
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
                if options.json:
                    print json.dumps({'name': c.name,
                                      'identifier': c.identifier})
                else:
                    print '%s (-c %s)' % (
                        c.name,
                        c.identifier)
            return

        try:
            self.converter_manager.get_by_id(options.converter)
        except KeyError:
            message = '%r is not a valid converter type.' % (
                options.converter,)
            if options.json:
                print json.dumps({'error': message})
            else:
                print 'ERROR:', message
                print 'Use "%s -l" to get a list of valid converters.' % (
                    parser.prog,)
                print
                parser.print_help()
            sys.exit(1)

        any_failed = False

        def changed(c):
            if c.status == 'failed':
                any_failed = True
            if options.json:
                output = {
                    'filename': c.video.filename,
                    'output': c.output,
                    'status': c.status,
                    'duration': c.duration,
                    'progress': c.progress,
                    'percent': (c.progress_percent * 100 if c.progress_percent
                                else 0),
                    }
                if c.error is not None:
                    output['error'] = c.error
                print json.dumps(output)
            else:
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

        for filename in args:
            try:
                c = app.start_conversion(filename, options.converter)
            except ValueError:
                message = 'could not parse %r' % filename
                if options.json:
                    any_failed = True
                    print json.dumps({'status': 'failed', 'error': message,
                                      'filename': filename})
                else:
                    print 'ERROR:', message
                continue
            changed(c)
            c.listen(changed)

        # XXX real mainloop
        while self.conversion_manager.running:
            self.conversion_manager.check_notifications()
            time.sleep(1)
        self.conversion_manager.check_notifications() # one last time

        sys.exit(0 if not any_failed else 1)

if __name__ == "__main__":
    initialize(None)
    app.widgetapp = Application()
    app.widgetapp.startup()
    app.widgetapp.run()

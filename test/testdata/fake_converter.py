import time
import sys
import os
import json

filename, output = sys.argv[1:3]
if 'error' in filename:
    print json.dumps({'finished': True, 'error': 'test error'})
    sys.exit(1)

if os.path.exists(output):
    print json.dumps({'finished': True,
                      'error': '%r existed when we started' % (
                output,)})
    sys.exit(1)

time.sleep(0.5)
RANGE = 5
for i in range(RANGE):
    print json.dumps({
            'filename': filename,
            'output': output,
            'duration': RANGE,
            'progress': i,
            'eta': RANGE - i
            })
    time.sleep(0.1)

with file(output, 'w') as f:
    f.write('blank')
print json.dumps({'finished': True})

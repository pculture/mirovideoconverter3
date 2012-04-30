import time
import sys
import json

filename, output = sys.argv[1:3]
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

#!/usr/bin/env python
import sys
from subprocess import Popen, PIPE

child = Popen([sys.executable, '-u', 'child.py'],
              stdin=PIPE, stdout=PIPE,
              bufsize=1, universal_newlines=True)
commandlist = ['Luke', 'Mike', 'Jonathan', 'Exit']
for command in commandlist:
    print('From PIPE: Q:', child.stdout.readline().rstrip('\n'))
    print(command, file=child.stdin)
    #XXX you might need it to workaround bugs in `subprocess` on Python 3.3
    #### child.stdin.flush()
    if command != 'Exit':
        print('From PIPE: A:', child.stdout.readline().rstrip('\n'))
child.stdin.close() # no more input
assert not child.stdout.read() # should be empty
child.stdout.close()
child.wait()
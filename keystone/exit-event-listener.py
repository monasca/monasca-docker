#!/usr/bin/env python
# coding=utf-8

# see also: http://stackoverflow.com/a/37527488
from __future__ import print_function

import os
import signal
import sys

from supervisor import childutils

PROCESS_NAME = 'keystone-bootstrap'


def main():
    while True:
        headers, payload = childutils.listener.wait()
        childutils.listener.ok()
        if headers['eventname'] != 'PROCESS_STATE_EXITED':
            continue

        phead, _ = childutils.eventdata(payload + '\n')
        if phead['processname'] == PROCESS_NAME and phead['expected'] == '0':
            print('Process {} failed, killing supervisord...'
                  .format(PROCESS_NAME), file=sys.stderr)

            # touch /kill-supervisor to tell wrapper script to exit uncleanly
            open('/kill-supervisor', 'w').close()

            os.kill(os.getppid(), signal.SIGTERM)


if __name__ == "__main__":
    main()

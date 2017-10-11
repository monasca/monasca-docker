#!/bin/sh

export LD_PRELOAD=/stack-fix.so
/sbin/tini -s -- "$@"

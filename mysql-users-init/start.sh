#!/bin/sh

LD_PRELOAD=/stack-fix.so python mysql_init.py

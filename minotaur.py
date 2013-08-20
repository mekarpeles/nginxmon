#-*- coding: utf-8 -*-
"""
    minotaur
    ~~~~~~~~

    A monitoring + email alert service for notifying/broadcasting
    nginx (and other service) errors via email.

    :copyright: (c) 2012 by Mek
    :license: BSD, see LICENSE for more details.
"""

import sys
import os
import datetime
import functools
import pyinotify
from mail import MailServer
from configs.config import service, email_creds

def tail( f, window=20 ):
    BUFSIZ = 1024
    f.seek(0, 2)
    bytes = f.tell()
    size = window
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if (bytes - BUFSIZ > 0):
            # Seek back one whole BUFSIZ
            f.seek(block*BUFSIZ, 2)
            # read BUFFER
            data.append(f.read(BUFSIZ))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            data.append(f.read(bytes))
        linesFound = data[-1].count('\n')
        size -= linesFound
        bytes -= BUFSIZ
        block -= 1
    return ''.join(data[::-1]).splitlines()[-window:]

def nginxmon_goalp(content):
    return False if any(["failed (2: No such file or directory)" in content]) \
        else True

def nginxmon_parser(logfile):
    """Returns the last entry from the nginx error.log file"""
    with open(logfile) as log:
        contents = tail(log)
        line = contents.pop()
        tmp = [line]
        while line.index(' ') == 0:
            line = contents.pop()
            tmp.append(line)
        return '\n'.join(tmp[::-1])
                
def callback(notifier, parser=None, goalp=None):
    content = parser() if parser else ''
    if goalp and not goalp(content):
        print("Skipping: %s" % content)
        return
    mailserver = MailServer(**email_creds)
    t = datetime.datetime.now().ctime()
    subject = "ERROR alert: (%s) at %s" % (service['name'], t)
    mailserver.sendmail(sender=mailserver.email, recipients=mailserver.email,
                        subject=subject, msg=content, fmt='plain')

def patrol(filename, event, success=callback, goalp=lambda *args, **kwargs: True):
    monitor = pyinotify.WatchManager()
    monitor.add_watch(filename, event)
    notifier = pyinotify.Notifier(monitor)
    
    while goalp(notifier):
        try:
            notifier.loop(daemonize=False, callback=callback,
                          pid_file='/tmp/pyinotify.pid', stdout='/tmp/stdout.txt')
        except pyinotify.NotifierError, err:
            print >> sys.stderr, err

if __name__ == "__main__":
    filename = service['logfile']
    event = getattr(pyinotify, service['event'], 'IN_MODIFY')
    parser = functools.partial(nginxmon_parser, filename)
    callback = functools.partial(callback, parser=parser, goalp=nginxmon_goalp)
    patrol(filename, event, success=callback)

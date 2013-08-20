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

def nginxmon(logfile):
    """Returns the last nginx error from the file"""
    with open(logfile) as log:        
        contents = tail(log)
        line = contents.pop()
        tmp = [line]
        while line.index(' ') == 0:
            line = contents.pop()
            tmp.append(line)
        return '\n'.join(tmp[::-1])
                
def event(notifier, mailserver, parser=None):
    t = datetime.datetime.now().ctime()
    subject = "ERROR alert: (%s) at %s" % (service['name'], t)
    msg = parser() if parser else ''
    mailserver.sendmail(sender=mailserver.email, recipients=mailserver.email,
                        subject=subject, msg=msg, fmt='plain')

if __name__ == "__main__":
    monitor = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(monitor)
    monitor.add_watch(service['logfile'], pyinotify.IN_CLOSE_WRITE)
    parser = functools.partial(nginxmon, service['logfile'])
    callback = functools.partial(event, mailserver=MailServer(**email_creds),
                                 parser=parser)
    while True:
        try:
            notifier.loop(daemonize=False, callback=callback,
                          pid_file='/tmp/pyinotify.pid', stdout='/tmp/stdout.txt')
        except pyinotify.NotifierError, err:
            print >> sys.stderr, err

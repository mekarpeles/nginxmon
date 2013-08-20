# -*- coding: utf-8 -*-

"""
    config.py
    ~~~~~~~~~

    This module is the middle man for handling/consolidating
    configurations for Minotaur.

    :copyright: (c) 2012 by Mek, Hackerlist
    :license: BSD, see LICENSE for more details.
"""

import ConfigParser
import os
import types

path = os.path.dirname(os.path.realpath(__file__))

def getdef(self, section, option, default_value, _type=None):
    try:
        v = self.get(section, option)
        return _type(v) if _type else v
    except:
        return default_value

config = ConfigParser.ConfigParser()
config.read('%s/minotaur.cfg' % path)
config.getdef = types.MethodType(getdef, config)

email_creds = {'email': config.getdef('mail', 'email', ''),
               'passwd': config.getdef('mail', 'passwd', ''),
               'host': config.getdef('mail', 'host', 'smtp.gmail.com'),
               'port': config.getdef('mail', 'port', 587, int)
               }

service = {'name': config.getdef('service', 'name', ''),
           'logfile': config.getdef('service', 'logfile', ''),
           'event': config.getdef('service', 'event', 'IN_MODIFY')
           }

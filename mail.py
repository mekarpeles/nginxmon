#-*- coding: utf-8 -*-
"""
    mail.py
    ~~~~~~~

    Send emails via smtp (using gmail, by default)

    :copyright: (c) 2012 by Mek
    :license: BSD, see LICENSE for more details.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.MIMEText import MIMEText

class MailServer(object):
    """Send mail via smtp (default gmail)

    usage:
    >>> from api.v1.mail import MailServer
    >>> ms = MailServer('mekarpeles@gmail.com', '********')
    >>> ms.sendmail(ms.email, recipients=['michael.karpeles@gmail.com'],
    ...                  subject='foobarbaz', msg='<b>test</b>', fmt="html")
    {}
    """

    def __init__(self, email, passwd, host='smtp.gmail.com', port=587):
        self.email = email
        self.server = smtplib.SMTP(host, port)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(email, passwd)

    def sendmail(self, sender, recipients='', subject='', msg='',
                 fmt='', method='smtp'):
        func = getattr(self, method, method)
        return func(sender, recipients, subject=subject, msg=msg, fmt=fmt)

    def smtp(self, sender, recipients='', subject='', msg='',
             fmt='', attatchment=None):
        mail = MIMEText() if not fmt else MIMEMultipart('alternative')
        mail['From'] = sender
        mail['To'] = recipients
        mail['Subject'] = subject
        if not fmt:
            mail.attach(MIMEText(msg, 'plain'))
        else:
            mail.attach(MIMEText(msg, 'html'))
        return self.server.sendmail(sender, recipients.split(','), mail.as_string())

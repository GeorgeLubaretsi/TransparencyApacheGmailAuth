#!/usr/bin/python

'''
Created on Nov 18, 2014

@author: msuliga
'''
import imaplib, getpass, re, ConfigParser, os, syslog

class GoogleImapAuth(object):
    '''
    The class logs in to a gmail account to check the credentials and logs out in case of success
    '''
    allowed_users_regex = ur'.*?@transparency\.ge$'
    imap_server = 'imap.googlemail.com'
    imap_port = 993
    syslog_enabled = True
    
    configuration_file =  os.path.dirname(os.path.realpath(__file__)) + '/gmauth.conf'
    
    os.path.dirname(os.path.realpath(__file__))
    
    def configure(self):
        defaults_file = '/etc/defaults/gmauth'
        if os.path.isfile( defaults_file):
            self.configuration_file = defaults_file
            
        config = ConfigParser.RawConfigParser( allow_no_value = False)
    
        config.read( self.configuration_file)
        self.allowed_users_regex = config.get('gmauth', 'allowed_users_regex')
        self.imap_server = config.get( 'gmauth', 'imap_server')
        self.imap_port = config.get( 'gmauth', 'imap_port')
        self.syslog_enabled = True if config.get( 'gmauth', 'syslog_enabled') == 'True' else False
        
    
    def authenticate(self, username_in, password_in):

        connGoogle = imaplib.IMAP4_SSL( self.imap_server, self.imap_port)
        try:
            connGoogle.login( username_in, password_in)
            connGoogle.logout()
            response = True
            if self.syslog_enabled:
                syslog.syslog( syslog.LOG_INFO, '[gmauth]: Authenticated user: %s on %s' % (username_in, self.imap_server))
        except imaplib.IMAP4_SSL.error:
            response = False
            if self.syslog_enabled:
                syslog.syslog( syslog.LOG_ERR, '[gmauth]: Failed to authenticate user: %s on %s' % (username_in, self.imap_server))
        return response

if __name__ == '__main__':
    
    # read username and passwd from console or stdin pipeline and authenticate
    
    username = getpass.getpass( 'Username: ')
    password = getpass.getpass( 'Password: ')
    
    auth = GoogleImapAuth()
    auth.configure()
    
    if not re.match( auth.allowed_users_regex, username):
        if auth.syslog_enabled:
            syslog.syslog( syslog.LOG_ERR, '[gmauth]: Forbidden user %s' % username)
        exit( 1)
    

    
    _ = exit(0) if auth.authenticate( username, password) else exit(1)

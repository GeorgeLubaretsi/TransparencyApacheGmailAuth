#!/usr/bin/python

'''
Created on Nov 18, 2014

@author: msuliga
'''
import imaplib, getpass, re, ConfigParser, os, syslog
import pickle, hashlib, datetime

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
    
    cache_file = '/tmp/.gmauth_cache'
    pass_cache = {}
    
    
    def configure(self):
        
        defaults_file = '/etc/default/gmauth'
        if os.path.isfile( defaults_file):
            self.configuration_file = defaults_file
            
        config = ConfigParser.RawConfigParser( allow_no_value = False)
    
        config.read( self.configuration_file)
        self.allowed_users_regex = config.get('gmauth', 'allowed_users_regex')
        self.imap_server = config.get( 'gmauth', 'imap_server')
        self.imap_port = config.get( 'gmauth', 'imap_port')
        self.syslog_enabled = True if config.get( 'gmauth', 'syslog_enabled') == 'True' else False
        
        self.load_cache()
    
    def load_cache(self):
        
        if not os.path.isfile( self.cache_file):
            return
        
        try: 
            cache_file = open( self.cache_file, 'rb')
            self.pass_cache = pickle.load( cache_file)
            cache_file.close()
        except IOError:
            pass
        
    def save_cache(self):
        
        cache_file = open( self.cache_file, 'wb')
        pickle.dump( self.pass_cache, cache_file)
        cache_file.close()
    
    def authenticate(self, username_in, password_in):
        
        if self.pass_cache.has_key( username_in):
            
            # discard cache older than a day
            date_hash = self.pass_cache[ username_in][1]
            date_today = datetime.date.today()
            
            #d_hash = datetime.datetime.strptime( date_hash, "%Y-%m-%d")
            #d_today = datetime.datetime.strptime( date_today, "%Y-%m-%d")
            
            date_diff = ( date_today - date_hash).days
            
            if date_diff > 1:
                return self.authenticate_gmail(username_in, password_in)
                
            hash_pass = hashlib.md5( password_in).digest()
            
            if hash_pass == self.pass_cache[ username_in][0]:
                syslog.syslog( syslog.LOG_INFO, '[gmauth]: Authenticated user: %s on %s' % (username_in, 'Auth Server'))
                return True
            else:
                return self.authenticate_gmail(username_in, password_in)
        else:
            return self.authenticate_gmail(username_in, password_in)

    def authenticate_gmail(self, username_in, password_in):

        connGoogle = imaplib.IMAP4_SSL( self.imap_server, self.imap_port)
        
        if self.pass_cache.has_key( username_in):
            del self.pass_cache[ username_in]
        
        try:

            connGoogle.login( username_in, password_in)
            connGoogle.logout()
            response = True
            # storing in cache
            self.pass_cache[ username_in] = (hashlib.md5( password_in).digest(), datetime.date.today())
 
        
            if self.syslog_enabled:
                syslog.syslog( syslog.LOG_INFO, '[gmauth]: Authenticated user: %s on %s' % (username_in, self.imap_server))
            
        except imaplib.IMAP4_SSL.error:
            response = False
            if self.syslog_enabled:
                syslog.syslog( syslog.LOG_ERR, '[gmauth]: Failed to authenticate user: %s on %s' % (username_in, self.imap_server))
        
        self.save_cache()
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

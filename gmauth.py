#!/usr/bin/python

'''
Created on Nov 18, 2014

@author: msuliga
'''
import imaplib, getpass, re

class GoogleImapAuth(object):
    '''
    The class logs in to a gmail account to check the credentials and logs out in case of success
    '''
    
    def authenticate(self, username_in, password_in):

        connGoogle = imaplib.IMAP4_SSL( 'imap.googlemail.com', 993)
        try:
            connGoogle.login( username_in, password_in)
            connGoogle.logout()
            response = True
        except imaplib.IMAP4_SSL.error:
            response = False
        return response

if __name__ == '__main__':
    
    # read username and passwd from console and authenticate
    
    username = getpass.getpass( 'Username: ')
    password = getpass.getpass( 'Password: ')
    
    if not re.match( ur'.*?@transparency\.ge', username):
        exit( 1)
    
    auth = GoogleImapAuth()
    _ = exit(0) if auth.authenticate( username, password) else exit(1)

# gmauth 
***

A simplistic program that authenticates apache2 using GMAIL IMAP.
This program only allows the users in transparency.ge domain to login.
It is designed to be used internally in Transparency International Georgia to secure access to files and other resources.


## Usage

* copy pwauth.py to /usr/local/bin/gmauth
* Configure Apache 

	ServerName server.domain

	Alias /authenticated	/file/system/location

	AddExternalAuth gmauth /usr/local/bin/gmauth
	SetExternalAuthMethod gmauth pipe

	<Directory /file/system/location>
	  AllowOverride AuthConfig
	  AuthType Basic
	  AuthName BaraBara
	  AuthBasicProvider external
	  AuthExternal gmauth
	  Require valid-user
	</Directory>

## requirements

* mod_authnz_external
* python 2.7
* urllib2, imaplib
* working Internet connection (there is no cache of any kind)

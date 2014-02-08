#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Written by Adam Cécile (Le_Vert) <acecile@le-vert.net>
#
# This is free software released into the public domain,
# or (at your option) under the terms of the WTFPL license (see below)
#
#
# DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
# Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
# DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
# TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
# 0. You just DO WHAT THE FUCK YOU WANT TO.


import sys
import hmac
import hashlib
from xml.dom.minidom import parseString

# Print to stderr function
def print_err(*args):
  sys.stderr.write(' '.join(map(str,args)) + '\n')

# python-requests
try:
  import requests
except:
  print_err('You must install Python "requests" module (http://pypi.python.org/pypi/requests)')
  print_err('Or try (Debian based systems): apt-get install python-requests')
  sys.exit(1)

# python-pyquery
try:
  from pyquery import PyQuery as pq
except:
  print_err('You must install Python "PyQuery" module (http://pypi.python.org/pypi/pyquery)')
  print_err('Or try (Debian based systems): apt-get install python-pyquery')
  sys.exit(1)


# Check arguments
import argparse
parser = argparse.ArgumentParser(description='This is a script to remotely reboot a SFR NeufBox 6')
parser.add_argument('-i','--ip', help='IP address of the router (ie: 192.168.1.1)',required=True)
parser.add_argument('-u','--user',help='Username to log into the Web management interface', required=True)
parser.add_argument('-p','--password',help='Password to log into the Web management interface', required=True)
args = parser.parse_args()

# Credentials
login = args.user
password = args.password
# Base URL
router = 'http://'+args.ip
# Reboot form URL
reboot_page = '/reboot'


# Special request to get a challenge key (authentication)
def getzsid(session):
  # God bless that guy who understood how NB authentication works...
  # http://lanterne-rouge.over-blog.org/article-neufboxwatcher-controlez-votre-box-avec-php-96128378.html
  challenge_headers = { 'X-Requested-With': 'XMLHttpRequest', 'X-Requested-Handler': 'ajax' }
  challenge_dict = {'action': 'challenge'}
  
  try:
    rep = session.post(router+'/login', data=challenge_dict, headers=challenge_headers)
  except Exception, e:
    print_err('HTTP connection to %s failed... Bad IP address ?' % router)
    print_err('The exception was: "%s"' % str(e))
    sys.exit(2)

  try:
    xml_dom = parseString(rep.text)
    zsid = xml_dom.getElementsByTagName('challenge')[0].firstChild.nodeValue
    # Unicode to string
    zsid = str(zsid)
  except Exception, e:
    print_err('Something gone wrong when trying to get challenge key for authentication')
    print_err('The exception was: "%s"' % str(e))
    sys.exit(3)

  return zsid

# sha256 string encode
def str2sha256(string):
  return hashlib.sha256(string).hexdigest()

# Generate authentication hash
def gethash(zsid, login, password):
  hash_login = hmac.new(zsid, str2sha256(login), hashlib.sha256).hexdigest()
  hash_password = hmac.new(zsid, str2sha256(password), hashlib.sha256).hexdigest()
  return hash_login+hash_password


# Use Chrome console (ctrl+shift+j), Network tab
# to find the form/post URL and dict parameters

# New session
s = requests.session()

# Get challenge key and create hash using login/password
zsid = getzsid(s)
hash = gethash(zsid, login, password)

# Ready to got !
auth_dict = {'method': 'passwd', 'page_ref': reboot_page, 'login': '', 'password': '', 'zsid': zsid, 'hash': hash }
cookies = { 'sid': zsid }

r = s.post(router+'/login', data=auth_dict, cookies=cookies)

# It may have worked...
if not r.status_code == 200:
  if r.status_code == 401:
    print_err('Got a HTTP/401 error while logging in... Bad password ?')
    sys.exit(4)
  else:
    print_err("Got a HTTP/%s error while logging in... That's weird..." % r.status_code)
    sys.exit(5)
  
# Let's reboot !
r = s.post(router+reboot_page, cookies=cookies)
if not r.status_code == 200:
  print_err("Got a HTTP/%s error when rebooting... That's weird..." % r.status_code)
  sys.exit(6)
else:
  print "Rebooting !"

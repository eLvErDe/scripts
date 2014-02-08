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
parser = argparse.ArgumentParser(description='This is a script to remotely reboot a NetGear CVBG834G router')
parser.add_argument('-i','--ip', help='IP address of the router (ie: 192.168.100.1 which is the hardcoded IP when running in bridged mode)',required=True)
parser.add_argument('-u','--user',help='Username to log into the Web management interface (default is "admin")', required=True)
parser.add_argument('-p','--password',help='Password to log into the Web management interface (default is "password")', required=True)
args = parser.parse_args()

# Credentials
login = args.user
password = args.password
r_auth = (login, password)
# Base URL
router = 'http://'+args.ip
# Reboot form URL
reboot_page = '/goform/NetGearMtaInfo'
# Status URL
status_page = '/NetGearMtaInfo.asp'

# Open session (cookie supported ?)
# Use Chrome console (ctrl+shift+j), Network tab
# to find the form/post URL and dict parameters
s = requests.session()
# Read status and convert into a PyQuery object
pq_status = pq(s.get(router+status_page, auth=r_auth).text)
# Get value of the form field
post_value = pq_status('input[name=NetgearCmLKFFrequency]').val()

# Change its value (otherwise it won't reboot)
if post_value[-1] == '0':
  post_value = int(post_value) + 1
else:
  post_value = int(post_value) - 1

# Create a post dictionnary
post_dict = {'NetgearCmLKFFrequency': str(post_value)}
# Post it to reboot URL (and pass auth again)
s.post(router+reboot_page, post_dict, auth=r_auth)


# Alternative code
# First try using urllib (works too but a lot more complicated)
#
#http_auth_realm = 'NETGEAR'
#import urllib2
#from urllib import urlencode
#
#auth_handler = urllib2.HTTPBasicAuthHandler()
#auth_handler.add_password(realm=http_auth_realm,
#                          uri=router,
#                          user=login,
#                          passwd=password)
#opener = urllib2.build_opener(auth_handler)
#
#urllib2.install_opener(opener)
#content = urllib2.urlopen(router+reboot_page,urlencode(post_dict))

#!/usr/bin/python

# WIP

import urllib2
import re
import sys
from pyquery import PyQuery as pq

base_url = 'http://forum.doom9.org/showthread.php?t=120988'

def read_url(url):
  req = urllib2.Request(url, headers={'User-Agent' : "Blu-Ray VUK grabber"})
  response = urllib2.urlopen(req)
  return response.read()

# Try to match number of pages like:
# <td class="vbmenu_control" style="font-weight:normal">Page 1 of 17</td>
base = read_url(base_url)
pq = pq(base)

# Should contains "Page 1 of 17"
page_of_max_page = pq(".vbmenu_control:last").text()

# Try to parse this one
max_page_re = re.match('^Page 1 of ([0-9]+)$', page_of_max_page)
if max_page_re:
  max_page = int(max_page_re.group(1))
  print "Doom9 forum thread has %s pages." % str(max_page)
else:
  print "Unable to find last page number"
  sys.exit(1)

r_keys = []
# Let's crawl against every pages
#for page in range(1, max_page+1):
for page in range(2, 3):

  sys.stdout.write("Processing page number %s... " % str(page))
  url = base_url+'&page='+str(page)
  pq = pq(read_url(url))
  pq_matches = pq("div[id^='post_message_']").text()

  nr_keys_added = 0

  for line in pq_matches.split('\n'):
  # Does each lines looks like being a Blu-Ray key ?
   if re.match('[0-9A-Z]{40}\s*=', line):
     print line
     line = re.sub(r'^.*([0-9A-Z]{40}\s*=)', r'\1', line)
     line = re.sub('\s+', ' ', line)
     line = line.strip()
     
     # Last sanity check
     if not re.match(r'^[0-9A-Z]{40}\s*=\s*.*|[0-9][0-9]/[0-9][0-9]/[0-9][0-9]|[0-9A-Z]{32}$', line): continue

     # Strip and create a dict
     key = line.split('=')[0]
     other = line.split('=')[1].split('|')
     other = [x.strip() for x in other]

     # Another sanity check :D
     if len(other) == 3:
       r_keys.append([key, other[0], other[1], other[2]])
       nr_keys_added += 1

  print str(nr_keys_added)+" keys found!"

# Display all keys :)
for key in r_keys:
  print key[0]+'='+key[1]+'|'+key[2]+'|'+key[3]

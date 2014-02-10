#!/usr/bin/python

# WIP

import urllib2
import re
import sys
from pyquery import PyQuery as pq
from pprint import pprint

base_url = 'http://forum.doom9.org/showthread.php?t=120988'

# Print to stderr function
def print_err(*args):
  sys.stderr.write(' '.join(map(str,args)))

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
  print_err("Doom9 forum thread has %s pages.\n" % str(max_page))
else:
  print_err("Unable to find last page number")
  sys.exit(1)

r_keys = []
total_keys = 0

# Let's crawl against every pages
for page in range(1, max_page+1):

  print_err("Processing page number %s... " % str(page))
  url = base_url+'&page='+str(page)
  pq = pq(read_url(url))
  pq_matches = str(pq("div[id^='post_message_']"))

  nr_keys_added = 0
 
  # Match any key
  # ie: C2871A3276BCD7C3174F5E6F5DD95D71CC3B957D=Tears of the Sun |00/00/00|B1444645B9481B0005F8BEF934970249
  # ie: 22F8CA73A81069F916B59C46FC7474D465C43F1E = Tomb Raider (US)    | D | 2006-09-26 | V | ABC2A63C40D0DE2068D302FA1B27C1DD | M | A04E521849100CC756C21827C1C8D7AF | I | A661C37014C571BC309A787588742E10
  key_matches = re.findall('[0-9A-Za-z]{40}\s*=.*[0-9A-Z]{32}', pq_matches)

  for key in key_matches:

    # Cleaning
    key = re.sub(r'(^.*[0-9A-Za-z]{32}).*$', r'\1', key)
    r_key = re.split('=|\|', key)
    r_key = [x.strip() for x in r_key]
    
    # Sanity check
    if len(r_key) >= 4:
      r_keys.append(r_key)
      nr_keys_added += 1
  
  print_err(str(nr_keys_added)+" keys found!\n")
  total_keys = total_keys + nr_keys_added

print_err("Total keys found: %s\n" % str(total_keys))
print_err("Without duplicates: %s\n" % str(len(r_keys)))

# Display all keys :)
for key in r_keys:
  key = ' | '.join(key)
  key = re.sub(r' \| ',' = ', key, 1)
  print key


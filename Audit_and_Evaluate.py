__author__ = 'kevinmcfarland'

'''
This code inspects the data for problematic characters in the tags
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re

OSM_file = 'bellevue_washington.osm'

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):                                            #counts the number of times each tag type occurs
    if element.tag == "tag":
        k_value = element.get("k")
        if re.search(lower, k_value):
            keys["lower"] += 1
        elif re.search(lower_colon, k_value):
            keys["lower_colon"] += 1
        elif re.search(problemchars, k_value):
            keys["problemchars"] += 1
            print k_value
        else:
            keys["other"] += 1
    return keys


def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys

def audit_key():
    keys = process_map(OSM_file)
    pprint.pprint(keys)

audit_key()

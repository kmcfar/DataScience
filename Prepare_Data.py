__author__ = 'kevinmcfarland'

import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json


problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

OSM_file = 'bellevue_washington.osm'


#lists and dictionary for updating street names
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons", "Center", "Circle", "Way", "Plaza", "Point"]

mapping = { "St": "Street",
            "St.": "Street",
            "ST": "Street",
            "Rd." : "Road",
            "Ave" : "Avenue",
            "CT" : "Court",
            "street" : "Street",
            "Av" : "Avenue",
            "PL" : "Place",
            "Ave." : "Avenue",
            "AVENUE" : "Avenue",
            "Blvd" : "Boulevard",
            "Blvd." : "Boulevard",
            "Sq" : "Square",
            "st" : "Street",
            "st." : "Street"
            }

#Compares street names against the expected list and updates any acronyms using the dictionary above
def update_streetname(street_name):
    auditkeys = mapping.keys()
    words = street_name.split()                         #cut street name into individual words
    for word in words:                                  #cycle through the words to check them against the dict values
        if word in auditkeys:
            words[words.index(word)] = mapping[word]
    words = " ".join(words)
    return words

#Cleans zipcodes to contain just the first five digits and to clear out any erroneous data
def update_zipcodes(k_value, v_value, node, zipcodes):
    long_zipcode = re.compile(r'\d{5}-\d{4}')
    combined_zipcodes = re.compile(r'[0-9]*;')
    correct_zipcode = re.compile(r'\d{5}')
    if k_value == "addr:postcode":                      #finds postcode values for nodes
        if re.match(long_zipcode, v_value):             #takes only the first five digits for zip codes in the form xxxxx-xxxx
            v_value = v_value[0:5]
        elif re.search('[a-zA-Z]', v_value):            #removes erroneous zipcodes where street names were put in as zipcodes
            v_value = None
        elif re.match(correct_zipcode, v_value):
            v_value = v_value
        return v_value
    elif re.match(r'tiger:zip', k_value):               #finds postcode values for ways
        if re.match(combined_zipcodes, v_value):        #takes only the first five digits for zip codes in the form xxxxx-xxxx
            v_value = v_value[0:5]
        else:
            v_value = v_value
        return v_value


#Cleans the address data and creates the address array
def clean_addresses(k_value, v_value, node, address):
    if not problemchars.match(k_value):
        node["address"] = address
        if re.search("postcode", k_value) or re.search("tiger:zip", k_value):       #cleans up zipcodes
            address["postcode"] = update_zipcodes(k_value, v_value, node, address)
        elif re.search("street", k_value):                                          #cleans up street names
            name = v_value
            better_name = update_streetname(name)
            if name != better_name:
                address["street"] = better_name
            else:
                address["street"] = name
        elif re.search("addr:", k_value):                                           #imports the other address fields
            address[k_value[5:]] = v_value
        else:
            node[k_value] = v_value

#Shapes the rest of the data and creates the documents
def shape_element(element):
    node = {}
    created_array = {}
    pos_array = []
    address = {}
    node_refs = []
    if element.tag == "node" or element.tag == "way" :                              #imports the values for node and way tags
        for tag in element.attrib:
            if tag in CREATED:
                created_array[tag] = element.attrib[tag]
                node["created"] = created_array
            elif tag == "lat" or tag == "lon":
                pos_array.insert(0, float(element.attrib[tag]))
                node["pos"] = pos_array
            elif tag == "id":
                node["id"] = element.attrib[tag]
            elif tag == "visible":
                node["visible"] = element.attrib[tag]

        for child in element:                                                       #cleans up and imports values of tags
            if child.tag == "tag":
                tag = child.attrib
                k_value = tag.get("k")
                v_value = tag.get("v")
                clean_addresses(k_value, v_value, node, address)
            if child.tag == "nd":
                ref_value = child.attrib["ref"]
                node_refs.append(ref_value)
                node["node_refs"] = node_refs

    if element.tag == "node":
        node["type"] = "node"
    if element.tag == "way":
        node["type"] = "way"

    pprint.pprint(node)
    return node

#Creates and outputs the JSON document by executing the above commands
def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def run():
    data = process_map(OSM_file, True)
    pprint.pprint(data)

run()

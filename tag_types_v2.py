
import xml.etree.cElementTree as ET
import pprint
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    #Count of each of four tag categories in a dict
    #Args: elements from the OpenStreetMap data and keys from the dict
    #Returns: A dict with the tag categories and their count
    if element.tag == "tag":
        if lower_colon.search(element.attrib['k']):
            keys['lower_colon'] += 1
        elif lower.search(element.attrib['k']):
            keys['lower'] += 1
        elif problemchars.search(element.attrib['k']):
            print("problem", element.attrib['k'])
            keys['problemchars'] += 1  
        else:
            keys['other'] += 1                  
    return keys


def process_map(filename):
    #Parses document 
    #Args: filename: OpenStreetMap data
    #Returns: keys: A dict with the tag categories and their count
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys

keys = process_map('rj_map.osm')
keys = process_map('sample_rj_map.osm')
pprint.pprint(keys)


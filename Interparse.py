
import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
    aux = set([])
    d = {} 
    
    #Find all the tags and how many of each
    #Args: filename: OpenStreetMap data
    #Returns: d: A dictionary with the tags and how many times they appear
    for event, elem in ET.iterparse(filename):
        if elem.tag in d:
            aux = int(d[elem.tag]) + 1
            d[elem.tag] = aux
        else:
            d.update({elem.tag:1})
            
    return d

tags = count_tags('rj_map.osm')
pprint.pprint(tags)
    
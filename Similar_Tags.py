import xml.etree.cElementTree as ET

#Parses file and corrects the not expected zip keys
#Args: 
    #osmfile: OpenStreetMap data
    #mapping: mapping dict with the problem types and the write ones
#Returns: street_types: A dict with the problem street types
    
OSMFILE = "rj_map.osm"

mapping = { 
           "CEP_LD": "zip:right",
           "CEP_LE": "zip:left",
           "cep:par": "zip:right",
           "cep:impar": "zip:left",
           "addr:zipcode": "addr:postcode"
            }

def audit(osmfile):
    #Parses file and calls audit_street_type function
    #Args: osmfile: OpenStreetMap data
    #Returns: street_types: A dict with the problem street types
    osm_file = open(osmfile, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                update_tags(tag, mapping)
    osm_file.close()


def update_tags(tag, mapping):
    postal_tag = tag.attrib['k']
    if tag.attrib['k'] in mapping:
        postal_tag = mapping[tag.attrib['k']]     
    return postal_tag                 

audit(OSMFILE)

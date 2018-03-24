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

def update(osmfile, mapping):
    osm_file = open(OSMFILE, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] in mapping:
                    tag.attrib['k'] = mapping[tag.attrib['k']]     
                    print(tag.attrib['k'])
    osm_file.close()                

update(OSMFILE, mapping)
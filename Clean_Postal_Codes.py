import xml.etree.cElementTree as ET
    
OSMFILE = "rj_map.osm"
#OSMFILE = "sample_rj_map.osm"
key_tags = ["zip:right", "zip:left", "addr:postcode" ]

def update_postal(spell):
    #Updates postal codes from the format XXXXXXXX to XXXXX-XXX
    #Args: spell: the attrib "v" from address:postcode
    #Returns: better_zip: zip code in the XXXXX-XXX format
    better_zip = spell
    if len(spell) == 8:
        better_zip = spell[0:5] + "-" + spell[5:8]                        
    return better_zip

def audit(osmfile, key_tags):
    #Parses file and calls update_postal
    #Args: 
        #osmfile: OpenStreetMap file
        #key_tags: the tags 'k' corresponding to the postal codes
    osm_file = open(OSMFILE, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] in key_tags:
                    update_postal(tag.attrib['v'])                    
    osm_file.close()                

audit(OSMFILE, key_tags)


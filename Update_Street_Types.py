import xml.etree.cElementTree as ET
from collections import defaultdict
import re

OSMFILE = "rj_map.osm"
#OSMFILE = "sample_rj_map.osm"
street_type_re = re.compile(r'^\b\S+\.?', re.IGNORECASE) #Street type is in the begining of the 
#street name in portuguese language

expected = ["Rua", "Avenida", "Acesso", "Calçadão", "Ladeira", "Praça", 
            "Travessa", "Via", "Vila", "Estrada", "Auto", "Alameda", "Aterro",
            "Beco", "Boulevard", "Caminho", "Largo", "Parque", "Praia", 
            "Rodovia", "Quadra", "Condominio", "Terminal"]

mapping = { "Av.": "Avenida",
           "Av": "Avenida",
           "av.": "Avenida",
           "Est.": "Estrada",
           "Estr.": "Estrada",
           "estrada": "Estrada",
           "PLAZA": "Praça",
           "Pca": "Praça",
           "Praca": "Praça",
           "Pça": "Praça",
           "Pça.": "Praça",
           "R.": "Rua",
           "Rod.": "Rodovia",
           "Ruas": "Rua",
           "Rue": "Rua",
           "Ruo": "Rua" ,
           "rua": "Rua",
           "vila": "Vila"
            }

def audit_street_type(street_types, street_name):
    #Creates a dict with all the street types that are not expected
    #Args:
        #street_types: a dict of sets 
        #street_name: a street name
    #Returns: street_types: A dict with the problem street types
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
    return street_types

def is_street_name(elem):
    #Returns true if the element key is "addr:street"
    #Args: elem: element of the OpenStreetMap data
    #Returns: true (is street) or false (is not street)
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    #Parses file and calls audit_street_type function
    #Args: osmfile: OpenStreetMap data
    #Returns: street_types: A dict with the problem street types
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

def update_name(name, mapping):
    #Corrects the not expected Street types
    #Args: 
        #name: street name
        #mapping: a mapping dict with the problem types and the write ones
    #Returns: better_name: The street name corrected
    m = street_type_re.search(name)
    better_name = name
    if m:
        better_street_type = mapping[m.group()]
        better_name = street_type_re.sub(better_street_type, name)
    return better_name

st_types = audit(OSMFILE)
for st_type, ways in st_types.items():
    for name in ways:
        try: #try except was used because of the street names that had no type
            better_name = update_name(name, mapping)
            print(name, ":", better_name)
        except KeyError:
            pass
            

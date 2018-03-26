# OpenStreetMap Data Case Study

This is a Udacity project for the module "Data Wrangling" of the "Data Science for Business" course. The goal of this project is to clean the OpenStreetMap data for Rio de Janeiro, RJ, Brazil.

## Map Area

Rio de Janeiro, RJ, Brazil 

https://www.openstreetmap.org/relation/2697338

https://overpass-api.de/api/map?bbox=-43.7997,-23.1157,-43.0959,-22.7129

I chose this area because this is the city I currently live in. It would be nice to have the opportunity to contribute to its improvement. 

## Problems Encountered in the Map

I noticed four main problems with the data, which I will discuss in the following order. Just keep in mind that names are in Portuguese, and thus the street names are called "Rua XXX", translating "Street XXX", and not " XXX Street" (the street types come first).

### 1. Over-abbreviated / Inconsistent street names 

Some Examples:

```Av``` and ```Av.``` meaning ```Avenida```

```Pça``` , ```Pça``` and ```Praca``` meaning ```Praça```

```R.```, ```Ruo``` and ```Rue``` meaning ```Rua```


### 2. Street Type missing 

See some examples bellow. All of them should have the street type before, i.e.,  "Rua …." or "Avenida ….." .

```
{'15': {'15 de Novembro'},
 '199': {'199'},
 'Afredo': {'Afredo Ceschiatti'},
 'Aires': {'Aires Itabaiana'},
 'Alfredo': {'Alfredo Ceschiatti'},
 'Apurinãs': {'Apurinãs'},
 'Arquias': {'Arquias Cordeiro'},
 'Assis': {'Assis Bueno'},
 'Augusta': {'Augusta Candiani'}, etc
 ```
 
### 3. Different key tags with the same meaning for postal codes

Some examples:

```CEP_LD``` vs ```cep:par``` vs ```zip:right```

```CEP_LE``` vs ```cep:impar```  vs ```zip:left```

```addr:zipcode``` vs ```addr:postcode```

### 4. Inconsistent postal codes

Example:

```22410-000``` vs ```22410000```

### 5. Inconsistent contact phones

```+55-21-9999-9999``` vs ```(21) 9999-9999``` vs ```9999-9999```, etc.

## Solving the problems

### 1. Over-abbreviated / Inconsistent street names 

```python
import xml.etree.cElementTree as ET
from collections import defaultdict
import re

OSMFILE = "rj_map.osm"
street_type_re = re.compile(r'^\b\S+\.?', re.IGNORECASE) 
#Street type is in the begining of the street name

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
        except KeyError:
            pass
```

https://github.com/danicastroaraujo/OpenStreetMap-DataWrangling/blob/master/Update_Street_Types.py

### 2. Street Type missing 

### 3. Different key tags with the same meaning for Postcodes

```python
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
```
https://github.com/danicastroaraujo/OpenStreetMap-DataWrangling/blob/master/Similar_Tags.py

### 4. Inconsistent postal codes

```python
import xml.etree.cElementTree as ET
    
OSMFILE = "rj_map.osm"

key_tags = ["zip:right", "zip:left", "addr:postcode" ]

def update_postal(spell):
    #Updates postal codes from the format XXXXXXXX to XXXXX-XXX
    #Args: spell: the attrib "v" from address:postcode
    #Returns: better_zip: zip code in the XXXXX-XXX format
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
```

### 5. Inconsistent contact phones

```python
import xml.etree.cElementTree as ET

OSMFILE = "rj_map.osm"

key_tags = ["phone" ]

def clean_phone(spell):
    #Removes special characters between phone numbers for uniformization
    fillers = [' ', '+', '-', '(', ')']
    disjunctions = [ '/', ',', 'ou' ]
    for i in range(len(fillers)):
        spell = spell.replace(fillers[i],'')
    for j in range(len(disjunctions)):
        spell = spell.replace(disjunctions[j],';')
    return spell

def update_phone(spell):
    #Updates phones to the format 
    #phone=+<country code> <area code> <local number>
    #following the ITU-T E.123 and the DIN 5008 pattern
    #Args: spell: the attrib "v" from <phone>
    #Returns: better_number: numbers in the right format
    better_number = str()
    spell = clean_phone(spell)
    if len(spell) == 12:
        #Updates complet phones to the right format
        better_number = '+' + spell[0:2] + ' ' + spell[2:4] + ' ' + spell[4:8] + '-' + spell[8:12]
    elif len(spell) == 13:
        #Updates complet cell phones to the right format
        better_number = '+' + spell[0:2] + ' ' + spell[2:4] + ' ' + spell[4:9] + '-' + spell[9:12] 
    elif len(spell) == 11 and spell[0] == '0':
        spell = spell[1:11] #remove 0 from code area
    elif len(spell) == 10 and spell[0:2] == '21': 
        #Updates phones with no country code to the right format
        better_number = '+55' + ' ' + spell[0:2] + ' ' + spell[2:6] + '-' + spell[6:10]
    elif len(spell) == 11 and spell[0:2] == '21': 
        #Updates cell phones with no country code to the right format
        better_number = '+55' + ' ' + spell[0:2] + ' ' + spell[2:7] + '-' + spell[7:11]
    elif len(spell) == 8:
        #Updates phones with no country code and no area code to the right format
        better_number = '+55 21 ' + spell[0:4] + '-' + spell[4:8]
    elif len(spell) == 9 and spell[0] == '9':
        #Updates cell phones with no country code and no area code to the right format
        better_number = '+55 21 ' + spell[0:5] + '-' + spell[5:9]
    elif spell[0:4] == '0800':
        better_number = spell[0:4] + '-' + spell[4:7] + '-' +  spell[7:11]
    elif ";" in spell: #Takes 'v' with more than one number
        if len(spell) == 25: #Complete two numbers
            better_number = '+' + spell[0:2] + ' ' + spell[2:4] + ' ' + spell[4:8] + '-' + spell[8:12] + ' ; ' + spell[13:15] + ' ' + spell[15:17] + ' ' + spell[17:21] + '-' + spell[21:25]
    else:
        print(spell, len(spell))
    return better_number

def audit(osmfile, key_tags):
    #Parses file and calls update_phone
    #Args: 
        #osmfile: OpenStreetMap file
        #key_tags: the tags 'k' corresponding to the phone numbers
    osm_file = open(OSMFILE, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] in key_tags:
                    update_phone(tag.attrib['v'])                    
    osm_file.close()     

audit(OSMFILE, key_tags)
```

https://github.com/danicastroaraujo/OpenStreetMap-DataWrangling/blob/master/Clean_Phone_Numbers.py

## Overview of the data

- The file has **280 MB**. 

- Number of ```unique users``` that have contributed to the map: **1703**

```python 
import xml.etree.cElementTree as ET

def get_user(element):
    #Gets users id from an element 
    #Arg: element: An element from the OpenStreetMap data
    #Returns: users: A set of the user ids    
    users = set([])
    if 'uid' in element.keys():
        users.add(element.attrib['uid'])
    return users
    
def process_map(filename):    
    #Parses document 
    #Args: filename: OpenStreetMap data
    #Returns: users: A set of the user ids    
    users = set([])
    for _, element in ET.iterparse(filename):
        users.update(get_user(element))
    return users

users = process_map('rj_map.osm')
print(len(users))
```

```python 
1703
```

https://github.com/danicastroaraujo/OpenStreetMap-DataWrangling/blob/master/number_users.py

- Number of ```tags```

```python 
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
```
```python 
{'bounds': 1,
 'member': 33214,
 'meta': 1,
 'nd': 1549891,
 'node': 1200106,
 'note': 1,
 'osm': 1,
 'relation': 3966,
 'tag': 595083,
 'way': 170480}
```
https://github.com/danicastroaraujo/OpenStreetMap-DataWrangling/blob/master/Interparse.py

- Number of ```k``` values for each ```tag```

```python 
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
pprint.pprint(keys)  
```
```python 
problem Conjunto Residencial
problem sub name
{'lower': 522194, 'lower_colon': 50664, 'other': 22223, 'problemchars': 2}
```
https://github.com/danicastroaraujo/OpenStreetMap-DataWrangling/blob/master/tag_types_v2.py


## References

https://forum.openstreetmap.org/viewtopic.php?id=61604

https://forum.openstreetmap.org/viewtopic.php?id=32037

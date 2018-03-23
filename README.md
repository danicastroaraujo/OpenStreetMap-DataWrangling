# OpenStreetMap Data Case Study

This is a Udacity project for the module "Data Wrangling" of the "Data Science for Business" course. The goal of this project was to use data munging techniques to clean the OpenStreetMap data for Rio de Janeiro, RJ, Brazil.

### Map Area

Rio de Janeiro, RJ, Brazil 

https://www.openstreetmap.org/relation/2697338

https://overpass-api.de/api/map?bbox=-43.7997,-23.1157,-43.0959,-22.7129

I chose this area because this is the city I currently live in. It would be nice to have the opportunity to contribute to its improvement. 

### Overview of the data

- The file has **280 MB**. 

- Number of unique users that have contributed to the map: **1703**

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

- Number of tags

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

- Number of "k" values for each "<tag>"

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


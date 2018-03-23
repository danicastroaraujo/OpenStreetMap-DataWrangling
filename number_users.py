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

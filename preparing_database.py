
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
#import schema

OSM_PATH = "rj_map.osm"
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


schema = {
    'node': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'lat': {'required': True, 'type': 'float', 'coerce': float},
            'lon': {'required': True, 'type': 'float', 'coerce': float},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'node_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    },
    'way': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'way_nodes': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'node_id': {'required': True, 'type': 'integer', 'coerce': int},
                'position': {'required': True, 'type': 'integer', 'coerce': int}
            }
        }
    },
    'way_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    }
}
            
SCHEMA = schema

# Make sure the fields order in the csvs matches the column order in the 
#sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 
               'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    node_child = {}#before tags
    way_child = {} #before way_nodes ans tags
    way_child2 = {} #before way_nodes ans tags
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    
    #List of attribs that are useful in nodes and way
    attribs_nodes = ["id", "user", "uid", "version", "lat", "lon", "timestamp",
                     "changeset"]
    attribs_way = ["id", "user", "uid", "version", "timestamp", "changeset"]
    
    if element.tag == 'node':
        for attrib in element.attrib:
            #Get only the attribs and texts in attribs_nodes
            if attrib in attribs_nodes: 
                node_attribs[attrib] = element.get(attrib)
        
        i = 0 
        #Get the child attribs 
        for child in element:
            i += 1
            #id: the top level node id attribute value
            node_child['id'] = element.get('id')

            #value: the tag "v" attribute value
            node_child['value'] = child.get('v')

            #key: the full tag "k" attribute value if no colon is present or 
            #the characters after 
            #the colon if one is.
            node_child['key'] = child.get('k')
            local_colon = node_child['key'].find(':')
            
            if local_colon > 0:
                aux = node_child['key']

                node_child['key'] = aux[local_colon+1:len(aux)]

                #type: either the characters before the colon in the tag "k" 
                #value or "regular" 
                #if a colon is not present.
                node_child['type'] = aux[0:local_colon]

            else:
                node_child['type'] = "regular"
            
            tags.append(node_child.copy())
            
        #if i == 0:
        #    tags.append({'value': '', 'type': '', 'id': element.get('id'), 
        #                'key': ''})
        
        return {'node': node_attribs, 'node_tags': tags}

        
    if element.tag == 'way':
        for attrib in element.attrib:
            #Get only the attribs and texts in attribs_way
            if attrib in attribs_way: 
                way_attribs[attrib] = element.get(attrib)

        
        position = 0 
        #Get the child attribs 

        for child in element:
            if child.tag == 'nd':
                way_child2['id'] = element.get('id') 
                way_child2['node_id'] = child.get('ref')
                way_child2['position'] = position
                position += 1
            
            if way_child2 not in way_nodes:
                way_nodes.append(way_child2.copy())
            
            i = 0 
            if child.tag == 'tag':
                #Get the child attribs 
                i += 1
                
                #id: the top level node id attribute value
                way_child['id'] = element.get('id')

                #value: the tag "v" attribute value
                way_child['value'] = child.get('v')

                #key: the full tag "k" attribute value if no colon is present 
                #or the characters after 
                #the colon if one is.
                way_child['key'] = child.get('k')
                local_colon = way_child['key'].find(':')

                if local_colon > 0:
                    aux = way_child['key']
                    way_child['key'] = aux[local_colon+1:len(aux)]

                    #type: either the characters before the colon in the tag 
                    #"k" value or "regular" 
                    #if a colon is not present.
                    way_child['type'] = aux[0:local_colon]

                else:
                    way_child['type'] = "regular"
                    
                tags.append(way_child.copy())
                
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
        

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, str) else v) for k, v 
            in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
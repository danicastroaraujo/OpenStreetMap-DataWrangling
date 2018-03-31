import xml.etree.cElementTree as ET

OSMFILE = "rj_map.osm"
#OSMFILE = "sample_rj_map.osm"

key_tags = ["phone"]

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
    #Parses file and calls update_postal
    #Args: 
        #osmfile: OpenStreetMap file
        #key_tags: the tags 'k' corresponding to the postal codes
    osm_file = open(OSMFILE, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] in key_tags:
                    update_phone(tag.attrib['v'])                    
    osm_file.close()     

audit(OSMFILE, key_tags)


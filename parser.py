import sys
import elementtree.ElementTree as etree

'''
    Structure of a configuration .xml file
    root node: config
    2nd node layer: interface/ldap
    3rd node layer: netword/dhcp/ppp (depends on value of interface type value)
    Note:
        if interface has eth* type node then can extract sub node network or not
        if ldap only get info
        if interface has based_on then extract info as sub dict of based_on value, if ethernet there will be sub node netword or dhcp or not
        if interface has ppp type node then extract info as sub dict of based_on value, there will be sub node ppp or network or not
'''
def config_parser(node, level, net_dict):

    # as default 'config' is the root node
    if node.tag : 
        conf_dict = {} # sub dict for config info
        for (name, value) in node.attrib.items():
            conf_dict[name] = value
        net_dict[node.tag] = conf_dict

        # since the next node right after the root 'config' node is main info for net_dict

        children0 = node.getchildren() # into 2nd node layer interface/ldap

        for child in children0:
            if child.tag == 'ldap': # extract ldap info
                net_dict[child.tag] = {}
                for (name, value) in child. attrib.items():
                    net_dict[child.tag][name] = value
            for (name, value) in child.attrib.items():
                if name == 'name' and 'eth' in value : # if interface has value of eth* then create a sub dict
                    net_dict[value] = {} # sub dict for network info of eth*
                    # check if there child node in interface
                    if child.getchildren():
                        for child1 in child.getchildren():
                            for (name1, value1) in child1.attrib.items():
                                if name1 != 'name' and name1 != 'comment':
                                    net_dict[value][name1] = value1

        for child in children0: # else check if inteface type node has based_on value or not
            sub_dict1 = {}
            pos_key = None
            add_key = None
            for (name, value) in child.attrib.items():
                if name == 'based_on': 
                    pos_key = value 
                    #print pos_key
                    for (name, value) in child.attrib.items():
                        if name == 'name':
                            add_key = value
                elif name != 'name' and name != 'comment':
                    sub_dict1[name] = value

            if child.getchildren(): # check if into 3rd node layer network/dhcp/ppp
                for child1 in child.getchildren():
                    sub_dict1[child1.tag] = {}
                    for (name1, value1) in child1.attrib.items():
                        if name1 != 'name' and name1 != 'comment':
                            sub_dict1[child1.tag][name1] = value1

            # then add sub dict at base_on value as key in net_dict
            if pos_key != None and add_key != None:
                net_dict[pos_key][add_key] = sub_dict1

        for child in children0: # interface has type value = ppp

            pos_key1 = None
            pos_key2 = None
            add_key = None

            for (name, value) in child.attrib.items():
                if name == 'name' and 'wan' in value: # check if interface has ppp type node 
                    add_key = value
                    sub_dict1 = {}
                    if child.getchildren(): # then check ppp sub node to get based_on value
                        for child1 in child.getchildren():
                            for (name, value) in child1.attrib.items():
                                if name == 'based_on':
                                    pos_key2 = value

                                    # find pos_key1 to add
                                    for key in net_dict.keys():
                                        for key1 in net_dict[key].keys():
                                            if key1 == pos_key2:
                                                pos_key1 =  key
                                elif name != 'name' and name != 'comment':
                                    sub_dict1[name] = value

                    # add into net_dict
                    net_dict[pos_key1][pos_key2][add_key] = sub_dict1

from pprint import pprint
def test(inFileName):
    doc = etree.parse(inFileName)
    root = doc.getroot()
    net_dict = {}
    config_parser(root, 0, net_dict)
    pprint(net_dict)

def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print 'usage: python test.py infile.xml'
        sys.exit(-1)
    test(args[0])

if __name__ == '__main__':
    main()

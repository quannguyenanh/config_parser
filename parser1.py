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

    type_list = [] # list of node type, stores 2 values: type value and base_on value

    # as default 'config' is the root node
    if node.tag == 'config' : 
        conf_dict = {} # sub dict for config info
        for (name, value) in node.attrib.items():
            conf_dict[name] = value
        net_dict[node.tag] = conf_dict

        # since the next node right after the root 'config' node is main info for net_dict

        children0 = node.getchildren() # into 2nd node layer interface/ldap
        add_key1 = None
        for child in children0:
            if child.tag == 'ldap': # extract ldap info
                net_dict[child.tag] = {}
                for (name, value) in child.attrib.items():
                    net_dict[child.tag][name] = value
            # else node layer is interface
            sub_dict1 = {}
            for (name, value) in child.attrib.items():
                if name == 'type': # if it has type value 
                    # then check if type value is first appear
                    for elm in type_list:
                        if elm[0] == value:
                            elm[1] += 1
                            break
                    else:
                        type_list.append([value, 1]) # if type is first then add to type list and count
                    # check if it has based_on value or not
                    found1 = False
                    found2 = False
                    for (name, value) in child.attrib.items():
                        if name == 'based_on':
                            found1 = True

                    if found1 == False: # if no based_on then check in its sub node if there is based_on value or not
                        if child.getchildren():
                                for child1 in child.getchildren():
                                    for (name, value) in child1.attrib.items():
                                        if name == 'based_on':
                                            found2 = True
                    if not found2 and not found1:# if no based_on at all then it will be a new sub dict
                        for (name, value) in child.attrib.items():
                            if name == 'name':
                                add_key1 = value
                            else:
                                if name != 'comment':
                                    sub_dict1[name] = value
                        # check if there child node in interface
                        if child.getchildren():
                            for child1 in child.getchildren():
                                for (name1, value1) in child1.attrib.items():
                                    if name1 != 'name' and name1 != 'comment':
                                        sub_dict1[name1] = value1
                        net_dict[add_key1] = sub_dict1
                    elif found1: # has based_on value in interface
                        # found key to add sub dict
                        sub_dict2 = {}
                        pos_key2 = None
                        add_key2 = None
                        for (name, value) in child.attrib.items():
                            if name == 'based_on': 
                                pos_key2 = value 
                                #print pos_key
                                for (name, value) in child.attrib.items():
                                    if name == 'name':
                                        add_key2 = value
                            elif name != 'name' and name != 'comment':
                                sub_dict2[name] = value
                        if child.getchildren(): # check if into 3rd node layer network/dhcp/ppp
                            for child1 in child.getchildren():
                                sub_dict2[child1.tag] = {}
                                for (name1, value1) in child1.attrib.items():
                                    if name1 != 'name' and name1 != 'comment':
                                        sub_dict2[child1.tag][name1] = value1

                        # then add sub dict at base_on value as key in net_dict
                        if pos_key2 != None and add_key2 != None:
                            net_dict[pos_key2][add_key2] = sub_dict2
                    elif not found1 and found2:
                        pos_key31 = None
                        pos_key32 = None
                        add_key3 = None

                        for (name, value) in child.attrib.items():
                            if name == 'name':
                                add_key3 = value

                                sub_dict3 = {}
                                if child.getchildren(): # then check sub node to get based_on value
                                    for child1 in child.getchildren():
                                        for (name, value) in child1.attrib.items():
                                            if name == 'based_on':
                                                pos_key32 = value

                                                # find pos_key31 to add
                                                for key in net_dict.keys():
                                                    for key1 in net_dict[key].keys():
                                                        if key1 == pos_key32:
                                                            pos_key31 =  key

                                            elif name != 'name' and name != 'comment':
                                                sub_dict3[name] = value

                        # add into net_dict
                        net_dict[pos_key31][pos_key32][add_key3] = sub_dict3

        for i in type_list:
            print i

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

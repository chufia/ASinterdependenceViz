#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 11:46:02 2018
"""
import requests
import gzip
import shlex, subprocess
import json
from datetime import date

desired_date = date(2018, 6, 19)
originAS = 28000

def getBaseVariables(desired_date, originAS):
    rrc00_bview_url = 'http://data.ris.ripe.net/rrc00/{}.{}/bview.{}.0800.gz'.format(desired_date.strftime('%Y'),
                                                                                     desired_date.strftime('%m'),
                                                                                     desired_date.strftime('%Y%m%d'))
    
    bview_file = 'bview_rrc00_{}_0800.gz'.format(desired_date.strftime('%Y%m%d'))
    
    hege_url = 'https://ihr.iijlab.net/ihr/api/hegemony/?originasn={}&timebin__gte={}+08:00&af=4'.format(originAS, desired_date)
    
    file_for_UI = 'input_for_UI.json'
    
    return rrc00_bview_url, bview_file, hege_url, file_for_UI

def getASpathsFromBview(bview_url, bview_file):
    r = requests.get(bview_url)
    open(bview_file, 'wb').write(r.content)
    
    bview_unzipped = '.'.join(bview_file.split('.')[:-1])
    
    with gzip.open(bview_file, 'rb') as f:
        open(bview_unzipped, 'wb').write(f.read())
    
    asPaths_file = 'ASpaths.txt'
    
    with open(asPaths_file, 'w') as asPaths_f:
        cmd = shlex.split('bgpdump -m {}'.format(bview_unzipped))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        
        cmd2 = shlex.split('cut -f 7 -d "|"')
        p2 = subprocess.Popen(cmd2, stdin=p.stdout, stdout=asPaths_f)
        
        p2.communicate()
    
        p.kill()
    
    return asPaths_file

def define_root(mnodes, root_asn=originAS):
    # In the UI we have the ability to centralise the root node. This function just
    # allows us to specifically configure the origin AS node independently
    mnodes[root_asn]['root'] = True
    mnodes[root_asn]['category'] = 'home'

    return mnodes

def classify_nodes(node_dict):
    # Can clean this up later but just a first pass at categorising the node based on
    # hemegeny. Size and other properties can then be configured as appropriate at the
    # UI
    for node in node_dict:
        hege = node_dict[node]["hege"]
        if hege == 0:
            category = 'xsmall'
        elif hege < 0.1:
            category = 'small'
        elif hege < 0.3:
            category = 'medium'
        elif hege < 0.6:
            category = 'large'
        elif hege >= 0.6 and hege < 0.9:
            category = 'xlarge'
        else:
            category = 'xxlarge'

        node_dict[node]["category"] = category

    return node_dict

def load_as_paths(input_file='all_as_paths.asc', asn=originAS):
    # From the list of all AS paths, import only the ones originating in the interesting AS
    as_paths = list()
    origin = str(asn)+'\n'
    for line in open(input_file, 'r'):
        if line.endswith(origin):
            as_paths.append(line.strip())
    return(as_paths)

def parse_as_paths(as_path_list):
    # From the list of originated paths, extract all nodes (unique ASs) and edges (unique 
    # connections between node pairs)
    nodes = dict()
    edges = list()

    for as_path in as_path_list:
        # each line represents the as-path for a route with the selected ASN as the originator. 

        # path needs to be manipulated from AS-Path to remove as-prepends as that's not a neighborship.
        # initialising as a list because a set doesn't respect sequence
        path = list()

        # Each entry in the AS-Path can be added to the nodes set so that we have a complete list of
        # all devices. As a set we don't need to check first, and don't care about sequence
        for node in as_path.split(' '):
            if not node == '':
                node = int(node.strip())
                nodes[node] = {'id': node, 'category': 0, 'label': '', 'hege': 0, 'distance': 100, 'root': False}
                if not node in path:
                    path.append(node)

        # Having worked through the AS-Path, and removed prepends, we can now consider the relationships.
        if len(path) > 1:
            # First the edges
            for i in range(len(path)-1):
                as_tuple = (path[i], path[i+1])
                dict_to_insert = {"source": min(as_tuple), "target": max(as_tuple)}
                if dict_to_insert not in edges:
                    edges.append(dict_to_insert)

            # And then the minimum distance from the AS
            for position, node in enumerate(path):
                nodes[node]['distance'] = min(nodes[node]['distance'], (len(path) - 1 - position))


    return( nodes, edges )

def getAShegeData(hege_url, mnodes):
    
    hege_json = requests.get(hege_url).json()
        
    for res in hege_json['results']:
        if res['asn'] not in mnodes:
            print("Ahhhhrrrrggghhhh")
        
        mnodes[res['asn']]['hege'] = res['hege']
        mnodes[res['asn']]['label'] = res['asn_name']
    
    return mnodes




def generateJSON(mnodes, medges):   
    json_UI_input = {'comment': 'AS interdependence Viz'}
    json_UI_input['nodes'] = list(mnodes.values())
    json_UI_input['edges'] = medges


#    with open(file_for_UI, 'w') as json_f:
#        json_f.write(json.dumps(json_UI_input))
#    
#    return file_for_UI
    return json.dumps(json_UI_input)

#rrc00_bview_url, bview_file, hege_url, file_for_UI = getBaseVariables(desired_date, originAS)
#asPaths_file = getASpathsFromBview(rrc00_bview_url, bview_file)
#as_paths = load_as_paths(asPaths_file, originAS)
#mnodes, medges = parse_as_paths(as_paths)
#mnodes = getAShegeData(hege_url, mnodes)
#mnodes = classify_nodes(mnodes)
#mnodes = define_root(mnodes, originAS)

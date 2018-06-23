#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 11:46:02 2018
"""
import requests
import gzip
import shlex, subprocess
from datetime import date
import json

desired_date = date(2018, 6, 19)

originAS = 28000

rrc00_bview_url = 'http://data.ris.ripe.net/rrc00/{}.{}/bview.{}.0800.gz'.format(desired_date.strftime('%Y'),
                                                                                 desired_date.strftime('%m'),
                                                                                 desired_date.strftime('%Y%m%d'))

bview_file = '/Users/sofia/Documents/GitHub/ASinterdependenceViz/bview_rrc00_{}_0800.gz'.format(desired_date.strftime('%Y%m%d'))

r = requests.get(rrc00_bview_url)
open(bview_file, 'wb').write(r.content)

bview_unzipped = '.'.join(bview_file.split('.')[:-1])

with gzip.open(bview_file, 'rb') as f:
    open(bview_unzipped, 'wb').write(f.read())

asPaths_file = '/Users/sofia/Documents/GitHub/ASinterdependenceViz/ASpaths.txt'

with open(asPaths_file, 'w') as asPaths_f:
    cmd = shlex.split('bgpdump -m {}'.format(bview_unzipped))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    
    cmd2 = shlex.split('cut -f 7 -d "|"')
    p2 = subprocess.Popen(cmd2, stdin=p.stdout, stdout=subprocess.PIPE)
    
    cmd3 = shlex.split('grep -e " {}$"'.format(originAS))
    p3 = subprocess.Popen(cmd3, stdin=p2.stdout, stdout=asPaths_f)

    p3.communicate()

    p2.kill()
    p.kill()
    

def parse_as_paths(input_file):

    nodes = set()
    edges = list()

    for as_path in open(input_file):
        # each line represents the as-path for a route with the selected ASN as the originator. 

        # path needs to be manipulated from AS-Path to remove as-prepends as that's not a neighborship.
        # initialising as a list because a set doesn't respect sequence
        path = list()

        # Each entry in the AS-Path can be added to the nodes set so that we have a complete list of
        # all devices. As a set we don't need to check first, and don't care about sequence
        for node in as_path.split(' '):
            if not node == '':
                nodes.add(int(node.strip()))
                if not node in path:
                    path.append(int(node.strip()))

        # Having worked through the AS-Path, and removed prepends, we can now consider the relationships.
        if len(path) > 1:
            for i in range(len(path)-1):
                as_tuple = (path[i], path[i+1])
                dict_to_insert = {"from": min(as_tuple), "to": max(as_tuple)}
                if dict_to_insert not in edges:
                    edges.append(dict_to_insert)

    return( nodes, edges )

mnodes, medges = parse_as_paths(asPaths_file)


hege_url = 'https://ihr.iijlab.net/ihr/api/hegemony/?originasn={}&timebin__gte={}+08:00&af=4'.format(originAS, desired_date)

hege_json = requests.get(hege_url).json()

nodes_dict = {}

for res in hege_json['results']:
    if res['asn'] not in nodes_dict:
        nodes_dict[res['asn']] = {}
    
    nodes_dict[res['asn']]['id'] = res['asn']
    nodes_dict[res['asn']]['hege'] = res['hege']
    nodes_dict[res['asn']]['label'] = res['asn_name']
    
for node in mnodes:
    if node not in nodes_dict:
        nodes_dict[node] = {'id':node, 'hege':0, 'label':''}


json_UI_input = {'comment': 'AS interdependence Viz'}
json_UI_input['nodes'] = list(nodes_dict.values())
json_UI_input['edges'] = medges

file_for_UI = '/Users/sofia/Documents/GitHub/ASinterdependenceViz/input_for_UI.json'
with open(file_for_UI, 'w') as json_f:
    json_f.write(json.dumps(json_UI_input))

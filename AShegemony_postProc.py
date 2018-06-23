#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 11:32:02 2018

@author: sofia
"""
import requests
from datetime import date

today = date.today()

originAS = 2914

hege_url = 'https://ihr.iijlab.net/ihr/api/hegemony/?originasn={}&timebin={}+08:00&af=4'.format(originAS,
                                                                                                today.strftime('%Y-%m-%d'))

hege_json = requests.get(hege_url).json()

nodes_dict = {}

for res in hege_json['results']:
    if res['asn'] not in nodes_dict:
        nodes_dict[res['asn']] = {}
    
    nodes_dict[res['asn']]['hege'] = res['hege']
    nodes_dict[res['asn']]['asn_name'] = res['asn_name']
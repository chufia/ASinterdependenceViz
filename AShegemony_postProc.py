#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 11:32:02 2018

@author: sofia
"""
import requests


hege_url = 'https://ihr.iijlab.net/ihr/api/hegemony/?originasn=2914&timebin__gte=2018-06-19+08:00&af=4'

hege_json = requests.get(hege_url).json()
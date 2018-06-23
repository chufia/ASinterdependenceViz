#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 11:46:02 2018

@author: sofia
"""
import requests
import gzip
import shlex, subprocess
from datetime import date

today = date.today()

originAS = 2914

rrc00_bview_url = 'http://data.ris.ripe.net/rrc00/{}.{}/bview.{}.0800.gz'.format(today.strftime('%Y'),
                                                                                 today.strftime('%m'),
                                                                                 today.strftime('%Y%m%d'))

bview_file = '/Users/sofia/Documents/GitHub/ASinterdependenceViz/bview_rrc00_{}_0800.gz'.format(today.strftime('%Y%m%d'))

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

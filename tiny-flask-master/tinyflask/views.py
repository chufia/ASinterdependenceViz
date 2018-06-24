from tinyflask import app
from tinyflask.config import app_globals
from ASinterdepViz import *

from flask import render_template
from datetime import date

desired_date = date(2018, 6, 19)
#originAS = 28000

rrc00_bview_url = 'http://data.ris.ripe.net/rrc00/{}.{}/bview.{}.0800.gz'.format(desired_date.strftime('%Y'),
                                                                                 desired_date.strftime('%m'),
                                                                                 desired_date.strftime('%Y%m%d'))

bview_file = 'bview_rrc00_{}_0800.gz'.format(desired_date.strftime('%Y%m%d'))

#asPaths_file = getASpathsFromBview(rrc00_bview_url, bview_file)
asPaths_file = '/Users/sofia/Documents/GitHub/ASinterdependenceViz/ASpaths.txt'

@app.route('/')
def index():
#    json_file = generateJSON(desired_date, originAS)
#    return render_template('index.html', globals=app_globals, json = json_file)
     return render_template('home.html', globals=app_globals)

@app.route('/originAS/<originAS>')
def getGraph(originAS):
    as_paths =  load_as_paths(asPaths_file, originAS)
    mnodes, medges = parse_as_paths(as_paths)

    hege_url = 'https://ihr.iijlab.net/ihr/api/hegemony/?originasn={}&timebin__gte={}+08:00&af=4'.format(originAS, desired_date)
    mnodes = getAShegeData(hege_url, mnodes)
    mnodes = classify_nodes(mnodes)
    mnodes = define_root(mnodes, int(originAS))
    return render_template('index.html', globals=app_globals, originAS = originAS, json=generateJSON(mnodes, medges))
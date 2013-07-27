# -*- coding: utf-8 -*-
from datetime import datetime
import re
import urllib
import urllib2
import HTMLParser
import pickle
import os.path as path
 
""" http://www.vigicrues.gouv.fr/niveau3.php?idstation=1750&idspc=21&typegraphe=h&AffProfondeur=72&AffRef=auto&AffPrevi=non&nbrstations=1&ong=2
 * idspc (service prévision des crues http://www.vigicrues.gouv.fr/niv_spc.php?idspc=19) pas nécessaire?
 * typegraphe= h (hauteur), d (débit)
 * AffProfondeur = nombre heures dans le passé (15 jours max?)
 * AffRef = afficher crues de références
 * AffPrevi
 * nbrstations
 * ong = 1 graphique, 2 = tableau, 3 = infos station
Check http://blog.dispatched.ch/2009/03/15/webscraping-with-python-and-beautifulsoup/?
"""

class scraper:
    def __init__(self,directory):
        self.directory = directory
    def load_stations(self):
        stations_path = path.join(self.directory,'stations.pkl')
        if path.exists(stations_path) :
            with open(stations_path, 'rb') as f :
                stations = pickle.load(f)
        else :
            ## Gathering static station informations by querying website with stations id from 0 to 1000
            stations = []
            for s in scraping.get_stations(range(0,10000)):
                stations.append(s)
                print s
            with open(stations_path, 'wb') as f :
                pickle.dump(stations, f)
        return stations
    def load_data(self):
        """
        Querying flow and heights for all stations.
        """
        flows_by_ids = dict()
        heights_by_ids = dict()

        for s in stations :
            flows_by_ids[s['id']] = scraping.get_flows(s['id'])
            heights_by_ids[s['id']] = scraping.get_heights(s['id'])
            print '{} heights and {} flows fetched for station {}'.format(len(heights_by_ids[s['id']]), len(flows_by_ids[s['id']]), s['id'])
        return flows_by_ids, heights_by_ids

def parse_station(page_text):
    """ Parse station features from html returned by url http://www.vigicrues.gouv.fr/niveau3.php?idstation=1516&idspc=21&typegraphe=h&AffProfondeur=72&AffRef=auto&AffPrevi=non&nbrstations=1&ong=3
    Station and stream's names, XY coordinates read from text,  station's code    deduced from link to hydro france website (http://www.hydro.eaufrance.fr/stations/Y3204030&procedure=fiche-station)

    >>> page_text = '''<div>
    ... <p><span class="titre_cadre">Station : </span>
    ... <span>Gourfaleur</span></p>
    ... 50</p>
    ... <p><span class="titre_cadre">Département : </span>
    ... <p>&nbsp;</p>
    ... <p><span class="titre_cadre">Cours d'eau : </span>
    ... <span>Vire</span></p>
    ... <p>&nbsp;</p>
    ... <p><span class="titre_cadre">Coordonnées Lambert II : </span>
    ... X=349486 m, Y=2459608 m</p>
    ... <p>&nbsp;</p>
    ... <p><span class="titre_cadre">Lien vers HydroWeb : </span>
    ... <a href="http://www.hydro.eaufrance.fr/stations/I5221010&amp;procedure=fiche-station" target="_blank">FICHE STATION</a>, <a href="http://www.hydro.eaufrance.fr/stations/I5221010&amp;procedure=synthese" target="_blank">SYNTHESE HYDROLOGIQUE</a> 
    ... </p>
    ... <p>&nbsp;</p><p><span class='titre_cadre'>Commentaires sur la station :</span><br />Les débits affichés sont des débits calculés à partir des courbes de tarage en vigueur.<br /></p></div>
    ... <div id="header"><ul><li><a href="./niveau3.php?idstation=1516&amp;idspc=4&amp;typegraphe=h&amp;AffProfondeur=168&amp;AffRef=auto&amp;AffPrevi=non&amp;nbrstations=4&amp;ong=1"><span>Graphique</span></a></li><li><a href="./niveau3.php?idstation=1516&amp;idspc=4&amp;typegraphe=h&amp;AffProfondeur=168&amp;AffRef=auto&amp;AffPrevi=non&amp;nbrstations=4&amp;ong=2"><span>Tableau</span></a></li><li id="current"><a href="./niveau3.php?idstation=1516&amp;idspc=4&amp;typegraphe=h&amp;AffProfondeur=168&amp;AffRef=auto&amp;AffPrevi=non&amp;nbrstations=4&amp;ong=3"><span>Infos station</span></a></li></ul></div>'''
    >>> parse_station(page_text)
    {'name': u'Gourfaleur', 'stream': u'Vire', 'Y': 2459608, 'X': 349486, 'spc': 4, 'id': 1516}
    """
    h = HTMLParser.HTMLParser()
    station = {}
    s = re.search('Station :.*\n.*<span>(.+)</span>', page_text)
    if s == None :
        return station
    else :
        station['name'] = unicode(h.unescape(s.groups()[0]))
    s = re.search("Cours d'eau :.*\n.*<span>(.+)</span>", page_text)
    if s == None :
        return station
    else :
        station['stream'] = unicode(h.unescape(s.groups()[0]))
    s = re.search("Coord.*\n.*X=(\d+).*Y=(\d+).*</p>", page_text)
    if s == None :
        return station
    else :
        station['X'] = int(s.groups()[0])
        station['Y'] = int(s.groups()[1])
    s = re.search(';idspc=(\d+)', page_text)
    if s == None :
        return station
    else :
        station['spc'] = int(s.groups()[0])
    s = re.search('idstation=(\d+)', page_text)
    if s == None :
        return station
    else :
        station['id'] = int(s.groups()[0])

    return station

def parse_flows(page_text):
    """
    Parse and returns time and flows array from page text
    >>> page_text = '''<area shape="poly" coords="405, 147, 409, 147, 409, 151, 405, 151, 405, 147" href="#0" title="27/02/2012 11:00 Valeur mesurée = 0.56" alt="27/02/2012 11:00 Valeur mesurée = 0.56" />'''
    >>> parse_flows(page_text)
    [(datetime.datetime(2012, 2, 27, 11, 0), 0.56)]
    """
    # Prefer to output list of tuples (dt,height), as it requires less processing AND is easily inserted into a pd.DataFrame through from_dict
    time_flow_tuples = [(datetime.strptime(m.groups()[0], '%d/%m/%Y %H:%M'), float(m.groups()[1])) for m in re.finditer("title=.?(.{16}) Valeur .* = (\d+\.?\d*)", page_text)]
    return time_flow_tuples
    # http://stackoverflow.com/questions/8081545/convert-list-of-tuples-to-multiple-lists-in-python
    #time_and_flows = map(list, zip(*time_flow_tuples))
    #return { "time":time_and_flows[0], "flow":time_and_flows[1]} if len(time_and_flows) != 0 else { "time":[],"flow":[]}

def get_flows(station_id):
    """
    Returns flows for a given station_id.
    Example with http://www.vigicrues.gouv.fr/niveau3.php?idstation=1516&typegraphe=q&AffProfondeur=500&ong=1
    >>> flows = get_flows(1516)
    """
    debitUrl = 'http://www.vigicrues.gouv.fr/niveau3.php?idstation={}&typegraphe=q&AffProfondeur=500&ong=1'
    flowGraphText = urllib2.urlopen(debitUrl.format(station_id)).read()
    return parse_flows(flowGraphText)

def parse_heights(page_text):
    """
    Parse and returns time and flows array from page text
    >>> page_text = '''<area shape="poly" coords="269, 123, 273, 123, 273, 127, 269, 127, 269, 123" href="#148" title="11/02/2013 06:00 Valeur mesurée = 1.95" alt="11/02/2013 06:00 Valeur mesurée = 1.95" />
    ... <area shape="poly" coords="270, 122, 274, 122, 274, 126, 270, 126, 270, 122" href="#149" title="11/02/2013 07:00 Valeur mesurée = 1.96" alt="11/02/2013 07:00 Valeur mesurée = 1.96" />'''
    >>> parse_heights(page_text)
    [(datetime.datetime(2013, 2, 11, 6, 0), 1.95), (datetime.datetime(2013, 2, 11, 7, 0), 1.96)]
    """
    # Prefer to output list of tuples (dt,height), as it requires less processing AND is easily inserted into a pd.DataFrame through from_dict
    time_height_tuples = [(datetime.strptime(m.groups()[0], '%d/%m/%Y %H:%M'), float(m.groups()[1])) for m in re.finditer("title=.?(.{16}) Valeur .* = (\d+\.?\d*)", page_text)]
    return time_height_tuples
    # http://stackoverflow.com/questions/8081545/convert-list-of-tuples-to-multiple-lists-in-python
    #time_and_heights = map(list, zip(*time_height_tuples))
    #return { "time":time_and_heights[0], "height":time_and_heights[1]}  if len(time_and_heights) != 0 else { "time":[],"height":[]}

def get_heights(station_id):
    """
    Returns heights for a given station_id.
    Example with http://www.vigicrues.gouv.fr/niveau3.php?idstation=1516&typegraphe=q&AffProfondeur=500&ong=1
    >>> heights = get_heights(1516)
    """
    hauteurUrl = 'http://www.vigicrues.gouv.fr/niveau3.php?idstation={}&typegraphe=h&AffProfondeur=500&ong=1'
    page_text = urllib2.urlopen(hauteurUrl.format(station_id)).read()
    return parse_heights(page_text)
     
def get_stations(station_ids, info_stations_url = 'http://www.vigicrues.gouv.fr/niveau3.php?idstation={}&ong=3'):
    """
    Get stations. safe catch to enable probing.
    >>> list(get_stations([1516]))[0]['name']
    u'Gourfaleur'
    """
    for id in station_ids :
        page_text = urllib2.urlopen(info_stations_url.format(id)).read()
        s = parse_station(page_text)
        if len(s) : 
            yield s
         
if __name__ == "__main__":
    import doctest
    doctest.testmod()
# -*- coding: utf-8 -*-
from datetime import datetime
import time
import re
import urllib, urllib2, json
import HTMLParser
import numpy as np

# Check http://blog.dispatched.ch/2009/03/15/webscraping-with-python-and-beautifulsoup/?

def parseStation(pageText):
    """ Parse station features from html returned by url http://www.vigicrues.gouv.fr/niveau3.php?idstation=1750&idspc=21&typegraphe=h&AffProfondeur=72&AffRef=auto&AffPrevi=non&nbrstations=1&ong=3
    Station and stream's names, XY coordinates read from text,  station's code    deduced from link to hydro france website (http://www.hydro.eaufrance.fr/stations/Y3204030&procedure=fiche-station)

    >>> pageText = '''<div>
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
    >>> parseStation(pageText)
    {'name': u'Gourfaleur', 'stream': u'Vire', 'Y': 2459608, 'X': 349486, 'spc': 4, 'id': 1516}
    """
    h = HTMLParser.HTMLParser()
    station = {}
    s = re.search('Station :.*\n.*<span>(.+)</span>', pageText)
    if s == None :
        return station
    else :
        station['name'] = unicode(h.unescape(s.groups()[0]))
    s = re.search("Cours d'eau :.*\n.*<span>(.+)</span>", pageText)
    if s == None :
        return station
    else :
        station['stream'] = unicode(h.unescape(s.groups()[0]))
    s = re.search("Coord.*\n.*X=(\d+).*Y=(\d+).*</p>", pageText)
    if s == None :
        return station
    else :
        station['X'] = int(s.groups()[0])
        station['Y'] = int(s.groups()[1])
    s = re.search(';idspc=(\d+)', pageText)
    if s == None :
        return station
    else :
        station['spc'] = int(s.groups()[0])
    s = re.search('idstation=(\d+)', pageText)
    if s == None :
        return station
    else :
        station['id'] = int(s.groups()[0])

    return station

# <area shape="poly" coords="405, 147, 409, 147, 409, 151, 405, 151, 405, 147" href="#0" title="27/02/2012 11:00 Valeur mesurée = 0.56" alt="27/02/2012 11:00 Valeur mesurée = 0.56" />
def getFlows(stationId):
    h = HTMLParser.HTMLParser()
    debitUrl = 'http://www.vigicrues.gouv.fr/niveau3.php?idstation={}&typegraphe=q&AffProfondeur=500&ong=1'
    flowGraphText = urllib2.urlopen(debitUrl.format(stationId)).read()
    tAndFs = np.array([(datetime.strptime(ts.groups()[0], '%d/%m/%Y %H:%M'), np.double(ts.groups()[1])) for ts in re.finditer("title=.?(.{16}) Valeur .* = (\d+\.?\d*)", flowGraphText)])
    return tAndFs
    #return (tAndFs[:,0],tAndFs[:,1]) if np.size(tAndFs) else (np.array([]),np.array([]))

def getHeights(stationId):
    h = HTMLParser.HTMLParser()
    hauteurUrl = 'http://www.vigicrues.gouv.fr/niveau3.php?idstation={}&typegraphe=h&AffProfondeur=500&ong=1'
    heightGraphText = urllib2.urlopen(hauteurUrl.format(stationId)).read()
    tAndHs = np.array([(datetime.strptime(ts.groups()[0], '%d/%m/%Y %H:%M'), np.double(ts.groups()[1])) for ts in re.finditer("title=.?(.{16}) Valeur .* = (\d+\.?\d*)", heightGraphText)])
    return tAndHs
    #return (tAndHs[:,0], tAndHs[:,1]) if np.size(tAndHs) else (np.array([]),np.array([]))
     

# Go through idStationRange and return station if found
def probeStations(idStationRange, infoStationsUrl = 'http://www.vigicrues.gouv.fr/niveau3.php?idstation={}&ong=3'):
    for idstation in idStationRange :
        infoStationsText = urllib2.urlopen(infoStationsUrl.format(idstation)).read()
        s = parseStation(infoStationsText)
        if len(s) : 
            yield s
            print s
        time.sleep(1)
         
if __name__ == "__main__":
    import doctest
    doctest.testmod()
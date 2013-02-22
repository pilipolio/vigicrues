# -*- coding: utf-8 -*-
import re
import urllib, urllib2, json
import HTMLParser
from datetime import datetime
import numpy as np

# <p><span class="titre_cadre">Station : </span>
	  # <span>Garigliano</span></p>

	  # <p><span class="titre_cadre">Département : </span>
	  # 34</p>
	  # <p>&nbsp;</p>

	  # <p><span class="titre_cadre">Cours d'eau : </span>
	  # <span>Lez</span></p>
	  # <p>&nbsp;</p>

	  # <p><span class="titre_cadre">Coordonnées Lambert II : </span>
	  # X=726099 m, Y=1847560 m</p>

def parseStation(txt):
	 h = HTMLParser.HTMLParser()
	 station = {}
	 s = re.search('Station :.*\r\n.*<span>(.+)</span>', txt)
	 if s == None :
		 return station
	 else :
		 station['name'] = h.unescape(s.groups()[0])
	 s = re.search("Cours d'eau :.*\r\n.*<span>(.+)</span>", txt)
	 if s == None :
		 return station
	 else :
		 station['stream'] = h.unescape(s.groups()[0])
	 s = re.search("Coord.*\r\n.*X=(\d+).*Y=(\d+).*</p>", txt)
	 if s == None :
		 return station
	 else :
		 station['X'] = s.groups()[0]
		 station['Y'] = s.groups()[1]
	 m = re.search(';idspc=(\d+)', txt)
	 if s == None :
		 return station
	 else :
		 station['spc'] = m.groups()[0]
	 m = re.search('idstation=(\d+)', txt)
	 if s == None :
		 return station
	 else :
		 station['id'] = m.groups()[0]
	 
	 return station

# <area shape="poly" coords="405, 147, 409, 147, 409, 151, 405, 151, 405, 147" href="#0" title="27/02/2012 11:00 Valeur mesurée = 0.56" alt="27/02/2012 11:00 Valeur mesurée = 0.56" />
def getFlows(stationId):
	 h = HTMLParser.HTMLParser()
	 debitUrl = 'http://www.vigicrues.gouv.fr/niveau3.php?idstation={}&typegraphe=q&AffProfondeur=500&ong=1'

	 flowGraphText = urllib2.urlopen(debitUrl.format(stationId)).read()
	 tAndFs = np.array([(datetime.strptime(ts.groups()[0], '%d/%m/%Y %H:%M'), np.double(ts.groups()[1])) for ts in re.finditer("title=.?(.{16}) Valeur .* = (\d+\.\d+)", flowGraphText)])
	 return (tAndFs[:,0],  tAndFs[:,1])

def getHeights(stationId):
	 h = HTMLParser.HTMLParser()
	 hauteurUrl = 'http://www.vigicrues.gouv.fr/niveau3.php?idstation={}&typegraphe=h&AffProfondeur=500&ong=1'

	 heightGraphText = urllib2.urlopen(hauteurUrl.format(stationId)).read()
	 tAndHs = np.array([(datetime.strptime(ts.groups()[0], '%d/%m/%Y %H:%M'), np.double(ts.groups()[1])) for ts in re.finditer("title=.?(.{16}) Valeur .* = (\d+\.\d+)", heightGraphText)])
	 return (tAndHs[:,0], tAndHs[:,1]) if np.size(tAndHs) else (np.array([]),np.array([]))

# Go through idStationRange and return station if found
def enumerateStations(idStationRange, infoStationsUrl = 'http://www.vigicrues.gouv.fr/niveau3.php?idstation={}&ong=3'):
	 maxStation = 10000
	 for idstation in range(maxStation) :
		 infoStationsText = urllib2.urlopen(infoStationsUrl.format(idstation)).read()
		 s = pageParser.parseStation(infoStationsText)
		 if len(s) : 
			 yield s
			 print s
		 time.sleep(1)
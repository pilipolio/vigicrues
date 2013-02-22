# -*- coding: utf-8 -*-
# http://www.vigicrues.gouv.fr/niv_spc.php?idspc=21
# www.hydro.eaufrance.fr/stations/Y2035010&procedure=fiche-station
# http://www.rdbrmc.com/hydroreel2/station.php?codestation=844
# http://www.languedoc-roussillon.developpement-durable.gouv.fr/telechargez-des-donnees-r514.html
# http://www.geolittoral.equipement.gouv.fr/comment-acceder-aux-donnees-via-r39.html
# http://eductice.ens-lyon.fr/EducTice/projets/en-cours/geomatique/veille/sig/Jeux-de-donnees

from datetime import datetime
import pickle
import numpy as np
from matplotlib import pyplot as plt
import vigicrues.scraping as scraping

## Gathering static station informations by querying website with stations id from 0 to 1000
stations = []
for s in scraping.get_stations(range(0,10000)):
    stations.append(s)
    print s

directory = r'D:\PythonWorkspace\site_packages\vigicrues\Data'
with open(directory + '/stations.pkl', 'wb') as f :
    pickle.dump(stations, f)

with open(directory + '/stations.pkl', 'rb') as f :
    stations = pickle.load(f)

## Querying flow and height
s = stations[0]
id = s['id']
id = 1516
t_fs = scraping.get_flows(id)
t_hs = scraping.get_heights(id)

fig = plt.figure()
ax = fig.add_subplot(111)
p_h = ax.plot(t_hs['time'], t_hs['height'],color='blue',lw=2,alpha=.7,label='Heights')
ax_f = ax.twinx()
p_f = ax_f.plot(t_fs['time'], t_fs['flow'],color='red',lw=2,alpha=.7,label='Flows')

p = plt.plot(tAndFs[:,0],tAndFs[:,1], label='Flow')
plt.twinx()
plt.plot(tAndHs[:,0],tAndHs[:,1], label='Height',c='r')
plt.title('{} ({})'.format(s['name'],s['stream']))
plt.legend()

## insert data into mongo
import pymongo
c = pymongo.Connection()
db = c.crues

for s in stations:
	 s['_id'] = s['id']
	 
db.stations.insert(stations)

stations = list(db.stations.find())

# fetch all heights
requestedDate = datetime.date(2012, 3, 11)
#db.heights.drop()
for s in stations:
	 #tAndFs = vigicrues.getFlows(s['id'])
	 ts,hs = vigicrues.getHeights(s['id'])
	 requestedIndexes = np.where(([t.date()==requestedDate for t in ts]))[0]
	 if (len(requestedIndexes)>0) : db.heights.insert({ 'id':s['id'], 't':ts[requestedIndexes[0]], 'h':hs[requestedIndexes[0]]})
	 print u'{} ({})'.format(s['name'],s['id'])
	 time.sleep(1)


hs = [h['h'] for h in db.heights.find({},{'h':1,'_id':0})]
plt.hist(hs,bins=np.arange(0,100,5))

plt.hist(hs,bins=10**np.linspace(-2, 2, 40))
plt.xscale('log')
plt.close()

scaleBins = np.array([-10000,0,0.1,0.3,1,3,10,30,100,10000])
scaleIntervals = np.array([np.array([b1,b2]) for b1, b2 in zip(scaleBins[:-1],scaleBins[1:])])
hsByInt = [[h for h in hs if (h >= b1 and h<b2)] for b1,b2 in scaleIntervals]

plt.hist(hsByInt,bins=10**np.linspace(-2, 2, 40)),labels=scaleIntervals)
plt.xscale('log')
plt.close()

# write csv X,Y,heights
def decorateHeight(h):
	 h.update(db.stations.find_one({'id':h['id']}))
	 h['hi'] = [i for i,bs in enumerate(scaleIntervals) if (h['h']>=bs[0] and h['h']<bs[1])][0]
	 return h
	 
decoratedHeights = map(decorateHeight, list(db.heights.find()))

with open(directory + '/heights.csv', 'wb') as f :
	 f.writelines((u'{};{};{};{}\r\n'.format(h['X'],h['Y'],h['h'],h['hi']) for h in decoratedHeights))

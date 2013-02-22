# -*- coding: utf-8 -*-
# http://www.vigicrues.gouv.fr/niv_spc.php?idspc=21
# http://www.hydro.eaufrance.fr/stations/Y2035010&procedure=fiche-station
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
for s in scraping.get_stations(range(10000,100000)):
    stations.append(s)
    print s

directory = r'D:\PythonWorkspace\site_packages\vigicrues\Data'
with open(directory + '/stations.pkl', 'wb') as f :
    pickle.dump(stations, f)

with open(directory + '/stations.pkl', 'rb') as f :
    stations = pickle.load(f)

## Querying flow and heights for all stations
import pandas as pd
flows_by_ids = dict()
heights_by_ids = dict()

for s in stations :
    #t_fs = scraping.get_flows(s['id'])
    #flows_by_ids[s['id']] =  pd.Series(t_fs['flow'],index=t_fs['time']) 
    #print '{0} flows fetched for station {1}'.format(len(t_fs['time']),s['id'])
    t_hs = scraping.get_heights(s['id'])
    heights_by_ids[s['id']] =  pd.Series(t_hs['height'],index=t_hs['time'])
    print '{0} heights fetched for station {1}'.format(len(t_hs['time']),s['id'])

# HDF5 storage of flows time series
store = pd.HDFStore('store.h5')
store['flows'] = pd.DataFrame(flows_by_ids)

df.ix[df.index[-1]]

# plot all stations with size depending on flows
import operator
import itertools
for stream,stream_stations in itertools.groupby(sorted(stations,key=operator.itemgetter('stream')),operator.itemgetter('stream')):
    plt.plot(*map(list,zip(*[(s['X'],s['Y']) for s in stream_stations])),color='grey')

plt.scatter(x=[s['X'] for s in stations],y=[s['Y'] for s in stations],s=np.log(df.ix[df.index[-100]]),edgecolor=None,color='grey',alpha=.75)

# Plot of flows and heights for a given station
fig = plt.figure()
ax_h = fig.add_subplot(111)
p_h = ax_h.plot(t_hs['time'], t_hs['height'],color='blue',lw=2,alpha=.7,label='Heights')
ax_h.legend(loc=2)
ax_f = ax_h.twinx()
p_f = ax_f.plot(t_fs['time'], t_fs['flow'],color='red',lw=2,alpha=.7,label='Flows')
ax_f.legend(loc=1)
for tick in ax_h.xaxis.get_major_ticks() : tick.label1.set_fontsize(6); tick.label1.set_rotation(30)

# heights histogram
plt.hist(hs,bins=10**np.linspace(-2, 2, 40))
plt.xscale('log')
plt.close()

scaleBins = np.array([-10000,0,0.1,0.3,1,3,10,30,100,10000])
scaleIntervals = np.array([np.array([b1,b2]) for b1, b2 in zip(scaleBins[:-1],scaleBins[1:])])
hsByInt = [[h for h in hs if (h >= b1 and h<b2)] for b1,b2 in scaleIntervals]

plt.hist(hsByInt,bins=10**np.linspace(-2, 2, 40)),labels=scaleIntervals)
plt.xscale('log')
plt.close()

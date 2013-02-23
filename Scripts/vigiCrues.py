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
import pandas as pd

directory = r'D:\PythonWorkspace\site_packages\vigicrues\Data'
scraper = scraping.scraper(directory)
stations = scraper.load_stations()

## Querying flow and heights for all stations
flows_by_ids = dict()
heights_by_ids = dict()

for s in stations[0:10] :
    flows_by_ids[s['id']] = scraping.get_flows(s['id'])
    heights_by_ids[s['id']] = scraping.get_heights(s['id'])
    print '{} heights and {} flows fetched for station {}'.format(len(heights_by_ids[s['id']]), len(flows_by_ids[s['id']]), s['id'])

heights = pd.DataFrame.from_dict(dict((id,dict(hs)) for id, hs in heights_by_ids.iteritems()),orient='columns')
flows = pd.DataFrame.from_dict(dict((id,dict(hs)) for id, hs in flows_by_ids.iteritems()),orient='columns')

# HDF5 storage of flows time series
store = pd.HDFStore(r'D:\PythonWorkspace\site_packages\vigicrues\Data\store.h5')
store['flows'] = flows
store['heights'] = heights

flows = store['flows']
heights = store['heights']

# Plot of flows and heights for a given station
station_id = 1516
fig = plt.figure()
ax_h = fig.add_subplot(111)
hs = heights[station_id][heights[station_id]>0]
p_h = ax_h.plot(hs.index,hs,color='blue',lw=2,alpha=.7,label='Heights')
ax_h.legend(loc=2)
ax_f = ax_h.twinx()
fs = flows[station_id][flows[station_id]>0]
p_f = ax_f.plot(fs.index,fs,color='red',lw=2,alpha=.7,label='Flows')
ax_f.legend(loc=1)
for tick in ax_h.xaxis.get_major_ticks() : tick.label1.set_fontsize(6); tick.label1.set_rotation(30)

# plot all stations with size depending on flows
import operator
import itertools
for stream,stream_stations in itertools.groupby(sorted(stations,key=operator.itemgetter('stream')),operator.itemgetter('stream')):
    plt.plot(*map(list,zip(*[(s['X'],s['Y']) for s in stream_stations])),color='grey',alpha=.25)

xys = [(s['X'],s['Y']) for s in stations]
cmap = mpl.ColorMap()
dt = pd.datetime(2013,02,06)
plt.scatter(*zip(*xys),s=flows.ix[dt],lw=0,c=np.log(heights.ix[dt]),alpha=.75)
plt.xticks([])
plt.yticks([])
plt.colorbar()

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

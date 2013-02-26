# -*- coding: utf-8 -*-
# http://www.vigicrues.gouv.fr/niv_spc.php?idspc=21
# http://www.hydro.eaufrance.fr/stations/Y2035010&procedure=fiche-station
# http://www.rdbrmc.com/hydroreel2/station.php?codestation=844
# http://www.languedoc-roussillon.developpement-durable.gouv.fr/telechargez-des-donnees-r514.html
# http://www.geolittoral.equipement.gouv.fr/comment-acceder-aux-donnees-via-r39.html
# http://eductice.ens-lyon.fr/EducTice/projets/en-cours/geomatique/veille/sig/Jeux-de-donnees

"""
TODO :
 * Start a notebook
 * analyze and fill missing values
 * calibration of heights/flows
 * animation of plots
 * match station to stream and geometry
 * build stream deformation according to flows/heights
 * flow/height relationship
"""
from datetime import datetime
from datetime import time
import pickle
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib as mpl
import vigicrues.scraping as scraping

directory = r'D:\PythonWorkspace\site_packages\vigicrues\Data'
scraper = scraping.scraper(directory)
stations = scraper.load_stations()

#heights = pd.DataFrame.from_dict(dict((id,dict(hs)) for id, hs in heights_by_ids.iteritems()),orient='columns')
#flows = pd.DataFrame.from_dict(dict((id,dict(hs)) for id, hs in flows_by_ids.iteritems()),orient='columns')

# HDF5 storage of flows time series
store = pd.HDFStore(r'D:\PythonWorkspace\site_packages\vigicrues\Data\store.h5')
#store['flows'] = flows
#store['heights'] = heights

flows = store['flows']
heights = store['heights']

# Missing data analysis : stations have a sampling period of 15/30/60min
count_by_times = flows.groupby(lambda ts : ts.time()).count().sum(axis=1)
plt.plot(count_by_times.index, count_by_times, color='grey',alpha=.8)
t_60mins = [t for t in count_by_times.index if t.minute == 0]
plt.plot(t_60mins, count_by_times[t_60mins],label='T=60  min')
t_30mins = [t for t in count_by_times.index if t.minute == 30]
plt.plot(t_30mins, count_by_times[t_30mins],label='T=30  min')
t_15_mins = [t for t in count_by_times.index if t.minute in [15,45]]
plt.plot(t_15_mins, count_by_times[t_15_mins],label='T=15  min')
plt.xticks([t for t in count_by_times.index if t.minute == 0],['{:%H}'.format(t) for t in count_by_times.index if t.minute == 0])
plt.legend()
plt.savefig('Sampling_periods.png')
plt.close()

# Re-indexing flows and heights to match the 60 min period and forward fill missing value with h = 
#flows = flows.reindex([t for t in flows.index if t.minute == 0])
flows = flows.resample('H',how='mean')
flows.fillna(method='ffill',limit=5,inplace=True)
#heights = heights.reindex([t for t in heights.index if t.minute == 0])
heights = heights.resample('H',how='mean')
heights.fillna(method='ffill',limit=5,inplace=True)

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
plt.savefig('station_heights_and_flows.png')

# Map of all stations with size depending on flows
import operator
import itertools
for stream,stream_stations in itertools.groupby(sorted(stations,key=operator.itemgetter('stream')),operator.itemgetter('stream')):
    plt.plot(*map(list,zip(*[(s['X'],s['Y']) for s in stream_stations])),color='grey',alpha=.25)

dt = pd.datetime(2013,02,12)
station_xys = [(s['X'],s['Y']) for s in stations]

plt.scatter(*zip(*station_xys),s=flows.ix[dt],lw=0,c=np.log(heights.ix[dt]),alpha=.75)
plt.xticks([])
plt.yticks([])
#plt.colorbar()
ax = plt.gca()
plt.setp(ax, frame_on=False)
plt.savefig('{:%Y%m%d}_France_maps.png'.format(dt))

# Bi-plot of flows/heights
#flows.ix[union_index].values.shape
#heights.ix[union_index].values.shape
union_index = flows.index.union(heights.index)
f_s = flows.ix[union_index].values
h_s = heights.ix[union_index].values
not_nan_idx = np.where(np.logical_not(logical_or(np.isnan(f_s),np.isnan(h_s))))
plt.scatter(f_s[not_nan_idx],h_s[not_nan_idx],alpha=.05,s=.3,c=not_nan_idx[1])
plt.ylim([0,15])
plt.xlim([0,2000])
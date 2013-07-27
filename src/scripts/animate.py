# -*- coding: utf-8 -*-
"""
Animation of heights/flows scatter plots.
http://jakevdp.github.com/blog/2012/08/18/matplotlib-animation-tutorial/
"""

from datetime import datetime
import pickle
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib import animation

import vigicrues.scraping as scraping

# # debug
# # set-up
# fig, ax = plt.subplots()
# x, y, s, c = next(x_y_s_cs)
# scat = ax.scatter(x, y, c=c, s=s)#, animated=True)
# ax.axis([np.min(x), np.max(x), np.min(y), np.max(y)])

# # update
# data = next(x_y_s_cs)
# # Set x and y data...
# scat.set_offsets(data[:2, :])
# # Set sizes...
# scat._sizes = data[2]
# # Set colors..
# scat.set_array(data[3])

class AnimatedScatter(object):
    """An animated scatter plot using matplotlib.animations.FuncAnimation.
    http://stackoverflow.com/questions/9401658/matplotlib-animating-a-scatter-plot
    """
    def __init__(self, x_y_s_c):
        self.stream = x_y_s_c
        # Setup the figure and axes...
        self.fig, self.ax = plt.subplots()
        # Then setup FuncAnimation.
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=5, init_func=self.setup_plot, blit=True)

    def setup_plot(self):
        """Initial drawing of the scatter plot."""
        x, y, s, c = next(self.stream)
        self.scat = self.ax.scatter(x, y, c=c, s=s, animated=True)
        self.ax.axis([np.min(x), np.max(x), np.min(y), np.max(y)])
        #self.ax.set_xticks([])
        #self.ax.set_yticks([])
        #plt.setp(self.ax, frame_on=False)

        # For FuncAnimation's sake, we need to return the artist we'll be using
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def update(self, i):
        """Update the scatter plot."""
        data = next(self.stream)

        # Set x and y data...
        #self.scat.set_offsets(data[:2, :])
        # Set sizes...
        self.scat._sizes = data[2]
        # Set colors..
        self.scat.set_array(data[3])

        print 'step {}, data[3,0] = {}'.format(i,data[3,0])
        # We need to return the updated artist for FuncAnimation to draw..
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

def get_x_y_s_c(dt) :
    x_y_s_c = np.zeros((4,(len(stations))))
    x_y_s_c[0,:] = zip(*station_xys)[0]
    x_y_s_c[1,:] = zip(*station_xys)[1]
    x_y_s_c[2,:] = flows.ix[dt]
    x_y_s_c[3,:] = np.log(heights.ix[dt])
    return x_y_s_c

if __name__ == '__main__':
    directory = r'D:\PythonWorkspace\site_packages\vigicrues\Data'
    scraper = scraping.scraper(directory)
    stations = scraper.load_stations()

    store = pd.HDFStore(r'D:\PythonWorkspace\site_packages\vigicrues\Data\store.h5')
    flows = store['flows']
    heights = store['heights']

    flows = flows.resample('H',how='mean')
    flows.fillna(method='ffill',limit=12,inplace=True)
    heights = heights.resample('H',how='mean')
    heights.fillna(method='ffill',limit=12,inplace=True)

    station_xys = [(s['X'],s['Y']) for s in stations]


    x_y_s_cs = (get_x_y_s_c(dt) for dt in heights.index if dt in heights.index and dt in flows.index)
    anim = AnimatedScatter(x_y_s_cs)
    plt.show()
#!/usr/bin/env python
from scipy.optimize import curve_fit
import time
import numpy as np
from operator import itemgetter, attrgetter
import libgraphite as lg
from  libgraphitestat.functions import *
from math import exp

class FrontStatModel():
    def __init__(self, debug, ylim = 0, graphite_server='bsgraphite.yandex-team.ru'):
        self.debug = debug
        self.ylim = ylim
        self.graphite_server = graphite_server

    def weight(self, d, x, y):
        radius = 50 # +-100 rps and ms
        count = 0
        for px,py in d:
            if px > (x-radius) and px < (x+radius):
                if py > (y-radius) and py < (y+radius):
                    count +=1
        return count

    def draw_single_graph(self, x, y, pfrom, title):
        self.pfrom = pfrom
        self.get_xy_data(x, y, pfrom)
        self.f = np.poly1d(np.polyfit(self.d[:,0], self.d[:,1], 5))
        self.single_raw_polyf_graph(title)
        return 1

    def draw_multi_graphs_weighted_polyf(self, x, y, pfrom, title):
        self.pfrom = pfrom
        self.get_xy_data(x, y, pfrom)
        self.multi_weighted_graph_polyf(title)
        return 1

    def multi_weighted_graph_polyf(self, title):
        self.set_default_params() # it will set internal vars xs, ylim and so on
        weighted_data = self.get_strong_points()
        self.f = np.poly1d(np.polyfit(weighted_data[:,0], weighted_data[:,1], 2))
        plt.plot(weighted_data[:,0],self.f(weighted_data[:,0]), label=title, linewidth=1)
        return 1

    def draw_multi_graphs_weighted(self, x, y, pfrom, title):
        self.pfrom = pfrom
        self.get_xy_data(x, y, pfrom)
        self.multi_weighted_graph(title)
        return 1

    def multi_weighted_graph(self, title):
        self.set_default_params() # it will set internal vars xs, ylim and so on
        weighted_data = self.get_strong_points()
        plt.plot(weighted_data[:,0],weighted_data[:,1], label=title, linewidth=1)
        return 1

    def get_fattest_point(self, r):
        radius_x = 20 # +-100 rps
        max_weight = 0
        max_x = 0
        max_y = 0
        d = self.d
        d_slice = d[ (d[:,0] > (r - radius_x)) & (d[:,0] < (r + radius_x))]
        for x, y in d_slice:
            w = self.weight(d_slice, x, y)
            if w > max_weight:
                max_weight = w
                (max_x, max_y) = (x, y)
                
        return (max_x, max_y, max_weight)

    def get_strong_points(self):
        rps_xs = np.linspace(self.d[:,0].min(), self.d[:,0].max(), 20)
        weighted_f = []
        for r in rps_xs:
            weighted_f.append(self.get_fattest_point(r))
        weighted_f = np.array(weighted_f)
        return  weighted_f 
     
    def draw_multi_graphs(self, x, y, pfrom, title):
        self.pfrom = pfrom
        self.get_xy_data(x, y, pfrom)
        self.f = np.poly1d(np.polyfit(self.d[:,0], self.d[:,1], 5))
        self.multi_polyf_graph(title)
        return 1

    def multi_polyf_graph(self, title):
        self.set_default_params() # it will set internal vars xs, ylim and so on
        plt.plot(self.d[:,0], self.f(self.d[:,0]), label=title, linewidth=1)
        return 1

    def draw_diff_polyf_graphs(self, sub, x,y, pfrom, title):
        self.pfrom = pfrom
        self.get_xy_data(x, y, pfrom)
        self.f = np.poly1d(np.polyfit(self.d[:,0], self.d[:,1], 2))
        res = [ [i, (self.f(i)/sub.f(i))] for i in self.d[:,0] ]
        plt.plot(self.d[:,0], res, label=title, linewidth=1)
        return 1

    def calculate_polyf(self, x, y, pfrom, delta):
        self.pfrom = pfrom
        self.get_xy_data(x, y, pfrom, delta)
        self.f = np.poly1d(np.polyfit(self.d[:,0], self.d[:,1], 5))
        return 1

    def get_xy_data(self, x_metric, y_metric, pfrom, delta=86400):
        x = np.array(graphite_data(self.graphite_server, x_metric, pfrom, pfrom + delta))
        y = np.array(graphite_data(self.graphite_server, y_metric, pfrom, pfrom + delta))
        if y.shape[0] != x.shape[0]:
            y = y[:x.shape[0]]
        d = np.column_stack((x,y))
        # reshape array using rps as key
        xy_arr = []
        for dp in d:
            for p in dp[1:]:
                xy_arr.append((dp[0],p))
        xy = np.array(xy_arr)
        self.d = np.array(sorted(xy, key=lambda a_entry: a_entry[0]))
        return 1

    def set_default_params(self):
        xmax = self.d[:,0].max()
#        if xmax < 1:
#            xmax = 1
#        elif xmax < 1000:
#            xmax = xmax + 100 - xmax % 100
#        elif xmax < 10000:
#            xmax = xmax + 1000 - xmax % 1000
#        elif xmax < 50000:
#            xmax = xmax + 5000 - xmax % 5000
        self.xs = np.linspace(0,xmax, 1000)
   # if ylim was passed as option, set max to passed ylim
        if self.ylim == 0:
            ymax = self.d[:,1].max()
            if ymax < 1:
                ymax = 1
            elif ymax < 2000:
                ymax = ymax + 100 - ymax % 100
            elif ymax < 10000:
                ymax = ymax + 1000 - ymax % 1000
            elif ymax < 50000:
                ymax = ymax + 5000 - ymax % 5000
            self.ylim = ymax
        return 1

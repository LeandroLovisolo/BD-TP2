#!/usr/bin/env python2

import matplotlib.pyplot as plt
import estimators
import performance

DATABASE    = 'custom.sqlite3'
TABLE       = 'data'
COL_UNIFORM = 'uniform'
COL_NORMAL  = 'normal'
PARAMETER   = 50

plt.rcParams['text.latex.preamble']=[r'\usepackage{lmodern}']
plt.rcParams.update({'text.usetex':         True,
                     'text.latex.unicode':  True,
                     'font.family':         'lmodern',
                     'font.size':           10,
                     'axes.titlesize':      10,
                     'legend.fontsize':     10,
                     'legend.labelspacing': 0.2})
fig = plt.figure()
fig.set_size_inches(6, 4)
plt.grid(True)
plt.tight_layout()

# ClassicHistogram
ch = estimators.ClassicHistogram(DATABASE, TABLE, COL_NORMAL, PARAMETER)
left = [bucket_range[0] for bucket_range in ch.bucket_ranges]
widths = [bucket_range[1] - bucket_range[0] for bucket_range in ch.bucket_ranges]
heights = ch.buckets
plt.bar(left, heights, width=widths, color='red', alpha=0.8)

# DistributionSteps
ds = estimators.DistributionSteps(DATABASE, TABLE, COL_NORMAL, PARAMETER)
left = ds.steps[:-1]
widths = [ds.steps[i + 1] - ds.steps[i] for i in range(0, ds.num_steps)]
heights = [ds.items_per_step for i in range(0, ds.num_steps)]
plt.bar(left, heights, width=widths, alpha=0.8)

plt.show()

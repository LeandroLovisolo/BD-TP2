#!/usr/bin/env python2

import sqlite3
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

NUM_BINS = 50
OUTPUT_BASE_FILENAME = '../tex/dataset-'

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

def get_column_names():
    column_names = []
    for row in c.execute('PRAGMA table_info(table1)'):
        column_names.append(row[1])
    return column_names

def plot_column(column):
    data = []
    for row in c.execute('select %s from table1' % column):
        data.append(row[0])

    # the histogram of the data
    n, bins, patches = plt.hist(data, NUM_BINS, normed=1, facecolor='green', alpha=0.75)

    plt.xlabel('Valor')
    plt.ylabel('Frecuencia')
    plt.title('Columna \emph{%s}' % column)
    #plt.axis([40, 160, 0, 0.03])
    plt.grid(True)

if __name__ == '__main__':
    plt.rcParams['text.latex.preamble']=[r'\usepackage{lmodern}']
    plt.rcParams.update({'text.usetex':         True,
                         'text.latex.unicode':  True,
                         'font.family':         'lmodern',
                         'font.size':           10,
                         'axes.titlesize':      10,
                         'legend.fontsize':     10,
                         'legend.labelspacing': 0.2})

    for column in get_column_names():
        fig = plt.figure()
        fig.set_size_inches(6, 4)

        print 'Plotting column %s...' % column
        plot_column(column)

        plt.tight_layout()
        plt.savefig(OUTPUT_BASE_FILENAME + column + '.pdf',
                    dpi=1000, box_inches='tight')
        #plt.show()

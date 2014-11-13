#!/usr/bin/env python2

import sqlite3
from plot import Plot

NUM_BINS = 50
OUTPUT_BASE_FILENAME = '../tex/dataset-'

class DatasetPlot(Plot):
    def __init__(self, conn, column):
        self.cursor = conn.cursor()
        Plot.__init__(self, OUTPUT_BASE_FILENAME + column + '.pdf')

    def do_plot(self, plt):
        data = []
        for row in self.cursor.execute('select %s from table1' % column):
            data.append(row[0])

        plt.hist(data, NUM_BINS, normed=1, facecolor='green', alpha=0.75)

        plt.xlabel('Valor')
        plt.ylabel('Frecuencia')

def get_column_names(conn):
    column_names = []
    for row in conn.cursor().execute('PRAGMA table_info(table1)'):
        column_names.append(row[1])
    return column_names

if __name__ == '__main__':
    conn = sqlite3.connect('db.sqlite3')

    for column in get_column_names(conn):
        print 'Plotting column %s...' % column
        DatasetPlot(conn, column)

    conn.close()

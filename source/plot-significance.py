#!/usr/bin/env python2
# coding: utf-8

import argparse
import sqlite3
from plot import Plot

DATABASE         = 'significance.sqlite3'
PVALUE_THRESHOLD = 0.05

class SignificancePlot(Plot):
    def __init__(self, data, output_path):
        self.data = data
        Plot.__init__(self, output_path)

    def do_plot(self, plt):
        for estimator1, estimator2, comparison, parameters, pvalues in self.data:
            label = '%s vs %s (%s)' % (estimator1, estimator2, comparison)
            plt.plot(parameters, pvalues, label=label)

        # Tomo los parametros de la primera comparación, asumiendo que todas
        # las comparaciones usan los mismos parameters.
        parameters = self.data[0][3]

        # Threshold
        plt.hlines(PVALUE_THRESHOLD, parameters[0], parameters[-1],
                   linestyle='--', color='b', alpha=0.4)

        # Pendiente: hacer funcionar el texto que acompaña a la línea de p-valor.
        # plt.text(PVALUE_THRESHOLD, parameters[1], 'p = %d' % PVALUE_THRESHOLD,
        #          verticalalignment='top', horizontalalignment='right')

        plt.xticks(parameters)
        plt.xlabel('Par\\\'ametro')
        plt.ylabel('p-valor')

        plt.legend()

def plot(column, output_path):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    plots = [('ClassicHistogram',  'DistributionSteps', 'equal'),
             ('ClassicHistogram',  'EstimadorGrupo',    'equal'),
             ('DistributionSteps', 'EstimadorGrupo',    'equal'),
             ('ClassicHistogram',  'DistributionSteps', 'greater'),
             ('ClassicHistogram',  'EstimadorGrupo',    'greater'),
             ('DistributionSteps', 'EstimadorGrupo',    'greater')]

    data = []
    for estimator1, estimator2, comparison in plots:
      parameters = []
      pvalues = []
      for row in c.execute('''  SELECT parameter1 AS parameter, pvalue
                                  FROM data
                                 WHERE column     = ?
                                   AND estimator1 = ?
                                   AND estimator2 = ?
                                   AND comparison = ?
                              ORDER BY parameter DESC''',
                           (column, estimator1, estimator2, comparison)):
        parameters.append(row[0])
        pvalues.append(row[1])
      data.append((estimator1, estimator2, comparison, parameters, pvalues))

    conn.close()

    SignificancePlot(data, output_path)
    exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates significance plots')

    parser.add_argument('column', metavar='COL', type=str,
                        help='which column to plot')
    parser.add_argument('-o', '--output')

    args = parser.parse_args()

    plot(args.column, args.output)

#!/usr/bin/env python2
# coding: utf-8

import argparse
import sqlite3
from plot import Plot

DATABASE = 'significance.sqlite3'

class SignificancePlot(Plot):
    def __init__(self, parameters_and_pvalues_per_column, output_path):
        self.parameters_and_pvalues_per_column = parameters_and_pvalues_per_column
        Plot.__init__(self, output_path)

    def do_plot(self, plt):
        # Asumo que se usan los mismos parámetros en todas las columnas.
        parameters = None

        for column, parameters, pvalues in self.parameters_and_pvalues_per_column:
            plt.plot(parameters, pvalues, label=column)

            plt.xticks(parameters)
            plt.xlabel('Par\\\'ametro')
            plt.ylabel('P-valor')

        length = max(parameters) - min(parameters)
        margin = length * 0.05
        plt.xlim([min(parameters) - margin, max(parameters) + margin])

        plt.legend()

def plot(estimator1, estimator2, comparison, output_path):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    columns = []
    for row in c.execute('''  SELECT DISTINCT(column)
                                FROM data
                               WHERE estimator1 = ?
                                 AND estimator2 = ?
                                 AND comparison = ?
                            ORDER BY column''',
                         (estimator1, estimator2, comparison)):
      columns.append(row[0])

    parameters_and_pvalues_per_column = []
    for column in columns:
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
      parameters_and_pvalues_per_column.append((column, parameters, pvalues))

    conn.close()

    SignificancePlot(parameters_and_pvalues_per_column, output_path)
    exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates performance plots')


    parser.add_argument('--hist-vs-diststep-equal',   action='store_true')
    parser.add_argument('--hist-vs-custom-equal',     action='store_true')
    parser.add_argument('--diststep-vs-custom-equal', action='store_true')

    parser.add_argument('--hist-vs-diststep-greater',   action='store_true')
    parser.add_argument('--hist-vs-custom-greater',     action='store_true')
    parser.add_argument('--diststep-vs-custom-greater', action='store_true')

    parser.add_argument('-o', '--output')

    args = parser.parse_args()

    if args.hist_vs_diststep_equal:
      plot('ClassicHistogram', 'DistributionSteps', 'equal', args.output)
    if args.hist_vs_custom_equal:
      plot('ClassicHistogram', 'EstimadorGrupo',    'equal', args.output)
    if args.diststep_vs_custom_equal:
      plot('DistributionSteps', 'EstimadorGrupo',   'equal', args.output)

    if args.hist_vs_diststep_greater:
      plot('ClassicHistogram', 'DistributionSteps', 'greater', args.output)
    if args.hist_vs_custom_greater:
      plot('ClassicHistogram', 'EstimadorGrupo',    'greater', args.output)
    if args.diststep_vs_custom_greater:
      plot('DistributionSteps', 'EstimadorGrupo',   'greater', args.output)

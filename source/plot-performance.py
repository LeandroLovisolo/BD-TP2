#!/usr/bin/env python2
# coding: utf-8

import argparse
import sys
import sqlite3
from plot import Plot
import numpy as np
import estimators
import performance

DATABASE    = 'custom.sqlite3'
TABLE       = 'data'
COL_UNIFORM = 'uniform'
COL_NORMAL  = 'normal'

class PerformancePlot(Plot):
    def __init__(self, parameters, means, stds, output_path):
        self.parameters = parameters
        self.means = means
        self.stds = stds
        Plot.__init__(self, output_path)

    def do_plot(self, plt):
        plt.errorbar(self.parameters, self.means, yerr=self.stds, marker='o')

        plt.xticks(self.parameters)
        plt.xlabel('Par\\\'ametro')
        plt.ylabel('Performance')

        length = max(self.parameters) - min(self.parameters)
        margin = length * 0.05
        plt.xlim([min(self.parameters) - margin, max(self.parameters) + margin])

def plot(estimator_class, distribution, comparison, output_path):
    parameters = range(5, 51, 5)
    column = COL_UNIFORM if distribution == 'uniform' else COL_NORMAL

    conn = sqlite3.connect(DATABASE)
    queries = performance.build_queries(conn.cursor(), TABLE, column, 50)
    conn.close()

    means = []
    stds = []

    current_parameter = 0
    for parameter in parameters:
        current_parameter += 1
        sys.stdout.write('\rComputig parameter %d/%d...' % (current_parameter, len(parameters)))
        sys.stdout.flush()

        estimator = estimator_class(DATABASE, TABLE, column, parameter)
        ground_truth = estimators.GroundTruth(DATABASE, TABLE, column, parameter)

        _, mean, std = performance.compute_performance(estimator, comparison, queries)

        means.append(mean)
        stds.append(std)

    sys.stdout.write('\n')
    PerformancePlot(parameters, means, stds, output_path)
    exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates performance plots')

    parser.add_argument('--hist-uniform-equal',   action='store_true')
    parser.add_argument('--hist-uniform-greater', action='store_true')
    parser.add_argument('--hist-normal-equal',    action='store_true')
    parser.add_argument('--hist-normal-greater',  action='store_true')

    parser.add_argument('--diststep-uniform-equal',   action='store_true')
    parser.add_argument('--diststep-uniform-greater', action='store_true')
    parser.add_argument('--diststep-normal-equal',    action='store_true')
    parser.add_argument('--diststep-normal-greater',  action='store_true')

    parser.add_argument('--custom-uniform-equal',   action='store_true')
    parser.add_argument('--custom-uniform-greater', action='store_true')
    parser.add_argument('--custom-normal-equal',    action='store_true')
    parser.add_argument('--custom-normal-greater',  action='store_true')

    parser.add_argument('-o', '--output')

    args = parser.parse_args()

    if args.hist_uniform_equal:
        plot(estimators.ClassicHistogram, 'uniform', 'equal', args.output)
    if args.hist_uniform_greater:
        plot(estimators.ClassicHistogram, 'uniform', 'greater', args.output)
    if args.hist_normal_equal:
        plot(estimators.ClassicHistogram, 'normal', 'equal', args.output)
    if args.hist_normal_greater:
        plot(estimators.ClassicHistogram, 'normal', 'greater', args.output)

    if args.diststep_uniform_equal:
        plot(estimators.DistributionSteps, 'uniform', 'equal', args.output)
    if args.diststep_uniform_greater:
        plot(estimators.DistributionSteps, 'uniform', 'greater', args.output)
    if args.diststep_normal_equal:
        plot(estimators.DistributionSteps, 'normal', 'equal', args.output)
    if args.diststep_normal_greater:
        plot(estimators.DistributionSteps, 'normal', 'greater', args.output)

    if args.custom_uniform_equal:
        plot(estimators.EstimadorGrupo, 'uniform', 'equal', args.output)
    if args.custom_uniform_greater:
        plot(estimators.EstimadorGrupo, 'uniform', 'greater', args.output)
    if args.custom_normal_equal:
        plot(estimators.EstimadorGrupo, 'normal', 'equal', args.output)
    if args.custom_normal_greater:
        plot(estimators.EstimadorGrupo, 'normal', 'greater', args.output)

#!/usr/bin/env python2
# coding: utf-8

import argparse
import sys
import sqlite3
import estimators
from plot import Plot
import numpy as np

class PerformancePlot(Plot):
    def __init__(self, bins, means, stds, output_path):
        self.bins = bins
        self.means = means
        self.stds = stds
        Plot.__init__(self, output_path)

    def do_plot(self, plt):
        plt.errorbar(self.bins, self.means, yerr=self.stds, marker='o')

        plt.xlabel('Par\\\'ametro')
        plt.ylabel('Performance')

def build_queries(column, n):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    c.execute('SELECT MIN(%s), MAX(%s) FROM table1' % (column, column))
    row = c.fetchone()
    min = row[0]
    max = row[1]
    step = (max - min) / n
    queries = range(min, max, step)

    conn.close()
    return queries

def plot(estimator_class, distribution, comparison, output_path):
    parameters = range(5, 51, 5)
    column = 'c0' if distribution == 'uniform' else 'c3'
    queries = build_queries(column, 50)

    means = []
    stds = []

    current_parameter = 0
    for parameter in parameters:
        current_parameter += 1
        sys.stdout.write('\rComputig parameter %d/%d...' % (current_parameter, len(parameters)))
        sys.stdout.flush()

        estimator = estimator_class('db.sqlite3', 'table1', column, parameter)
        ground_truth = estimators.GroundTruth('db.sqlite3', 'table1', column, parameter)

        if comparison == 'equal':
            estimations = [estimator.estimate_equal(q) for q in queries]
            truths      = [ground_truth.estimate_equal(q) for q in queries]
        else:
            estimations = [estimator.estimate_greater(q) for q in queries]
            truths      = [ground_truth.estimate_greater(q) for q in queries]

        estimations = np.array(estimations)
        truths = np.array(truths)
        performances = np.absolute(estimations - truths)

        mean = np.mean(performances)
        std = np.std(performances)

        means.append(mean)
        stds.append(std)

    sys.stdout.write('\n')

    PerformancePlot(parameters, means, stds, output_path)

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
        exit()
    if args.hist_uniform_greater:
        plot(estimators.ClassicHistogram, 'uniform', 'greater', args.output)
        exit()
    if args.hist_normal_equal:
        plot(estimators.ClassicHistogram, 'normal', 'equal', args.output)
        exit()
    if args.hist_normal_greater:
        plot(estimators.ClassicHistogram, 'normal', 'greater', args.output)

    if args.diststep_uniform_equal:
        plot(estimators.DistributionSteps, 'uniform', 'equal', args.output)
        exit()
    if args.diststep_uniform_greater:
        plot(estimators.DistributionSteps, 'uniform', 'greater', args.output)
        exit()
    if args.diststep_normal_equal:
        plot(estimators.DistributionSteps, 'normal', 'equal', args.output)
        exit()
    if args.diststep_normal_greater:
        plot(estimators.DistributionSteps, 'normal', 'greater', args.output)
        exit()

    if args.custom_uniform_equal:
        plot(estimators.EstimadorGrupo, 'uniform', 'equal', args.output)
        exit()
    if args.custom_uniform_greater:
        plot(estimators.EstimadorGrupo, 'uniform', 'greater', args.output)
        exit()
    if args.custom_normal_equal:
        plot(estimators.EstimadorGrupo, 'normal', 'equal', args.output)
        exit()
    if args.custom_normal_greater:
        plot(estimators.EstimadorGrupo, 'normal', 'greater', args.output)
        exit()

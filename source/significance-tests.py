#!/usr/bin/env python2
# coding: utf-8

import sqlite3
from scipy import stats
import estimators
import performance

DATABASE    = 'db.sqlite3'
TABLE       = 'table1'
NUM_QUERIES = 50

def parameters_for(estimator_class):
    return [10, 50, 100]

for column in ['c%d' % i for i in range(0, 10)]:
    conn = sqlite3.connect(DATABASE)
    queries = performance.build_queries(conn.cursor(), TABLE, column, NUM_QUERIES)
    conn.close()

    for bins in parameters_for(estimators.ClassicHistogram):
        for steps in parameters_for(estimators.DistributionSteps):
            e1 = estimators.ClassicHistogram(DATABASE, TABLE, column, bins)
            e2 = estimators.DistributionSteps(DATABASE, TABLE, column, steps)

            performances_e1, mean_e1, _ = performance.compute_performance(e1, 'equal', queries)
            performances_e2, mean_e2, _ = performance.compute_performance(e2, 'equal', queries)

            _, p_value = stats.ttest_rel(performances_e1, performances_e2)

            print "column: %s\tbins: %d\tsteps: %d\tmean CH: %f\tmean DS: %f\tp-value: %f" \
                    % (column, bins, steps, mean_e1, mean_e2, p_value)

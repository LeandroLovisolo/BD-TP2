#!/usr/bin/env python2
# coding: utf-8

import sqlite3
from scipy import stats
import estimators
import performance

DATABASE    = 'db.sqlite3'
TABLE       = 'table1'
NUM_QUERIES = 50

def parameters_for(estimator1_class, estimator2_class):
    return [i for i in range(10, 110, 10)]

def queries_for(column):
    conn = sqlite3.connect(DATABASE)
    queries = performance.build_queries(conn.cursor(), TABLE, column, NUM_QUERIES)
    conn.close()
    return queries

if __name__ == '__main__':
    columns = ['c%d' % i for i in range(0, 10)]
    estimator_pairs = [(estimators.ClassicHistogram, estimators.DistributionSteps),
                       (estimators.ClassicHistogram, estimators.EstimadorGrupo),
                       (estimators.DistributionSteps, estimators.EstimadorGrupo)]

    conn = sqlite3.connect('significance.sqlite3')
    c = conn.cursor()

    c.execute('DROP TABLE IF EXISTS data')
    c.execute('''
              CREATE TABLE data (column     INTEGER,
                                 comparison TEXT,
                                 estimator1 TEXT,
                                 estimator2 TEXT,
                                 parameter1 INTEGER,
                                 parameter2 INTEGER,
                                 mean1      REAL,
                                 mean2      REAL,
                                 pvalue     REAL)
              ''')

    for column in columns:
        for comparison in ['equal', 'greater']:
            for estimator1_class, estimator2_class in estimator_pairs:
                queries = queries_for(column)
                for parameter in parameters_for(estimator1_class, estimator2_class):
                    e1 = estimator1_class(DATABASE, TABLE, column, parameter)
                    e2 = estimator2_class(DATABASE, TABLE, column, parameter)

                    performances_e1, mean_e1, _ = performance.compute_performance(e1, comparison, queries)
                    performances_e2, mean_e2, _ = performance.compute_performance(e2, comparison, queries)

                    _, p_value = stats.ttest_rel(performances_e1, performances_e2)

                    print 'column: %s\tcomparison: %s\test1: %s\test2: %s\tparam1: %d\tparam2: %d\tmean1: %f\tmean2: %f\tp-value: %f' \
                            % (column,
                               comparison,
                               estimator1_class.__name__,
                               estimator2_class.__name__,
                               parameter, parameter,
                               mean_e1, mean_e2,
                               p_value)

                    c.execute('INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            (column,
                             comparison,
                             estimator1_class.__name__,
                             estimator2_class.__name__,
                             parameter, parameter,
                             mean_e1, mean_e2,
                             p_value))

    conn.commit()
    conn.close()


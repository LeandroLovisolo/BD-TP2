import numpy as np
import estimators

def build_queries(cursor, table, column, n):
    cursor.execute('SELECT MIN(%s), MAX(%s) FROM %s' % (column, column, table))
    row = cursor.fetchone()
    min = row[0]
    max = row[1]
    step = (max - min) / n
    queries = range(min, max, step)
    return queries

def compute_performance(estimator, comparison, queries):
    ground_truth = estimators.GroundTruth(estimator.db,
                                          estimator.table,
                                          estimator.column)

    def estimate(estimator, query):
        if comparison == 'equal': return estimator.estimate_equal(query)
        else:                     return estimator.estimate_greater(query)

    estimations = np.array([estimate(estimator, q)    for q in queries])
    truths      = np.array([estimate(ground_truth, q) for q in queries])

    performances = np.absolute(estimations - truths)
    mean = np.mean(performances)
    std = np.std(performances)

    return (performances, mean, std)




# -*- coding: utf-8 -*-

import estimators
import random

def test_estimators(steps, column, total_values=100):
    a_estimator = estimators.ClassicHistogram('db.sqlite3', 'table1', column, parameter=steps)
    b_estimator = estimators.DistributionSteps('db.sqlite3', 'table1', column, parameter=steps)
    c_estimator = estimators.EstimadorGrupo('db.sqlite3', 'table1', column, parameter=steps)
    d_estimator = estimators.GroundTruth('db.sqlite3', 'table1', column, parameter=steps)

    val_range = a_estimator.max - a_estimator.min

    values = []
    for i in xrange(total_values):
        values.append(random.randint(a_estimator.min, a_estimator.max))

    error_a_eq = 0
    error_b_eq = 0
    error_c_eq = 0
    error_a_gt = 0
    error_b_gt = 0
    error_c_gt = 0

    for value in values:
        # print "-------------------------------------%s-------------------------------------" % str(value)
        # print "Classic Histogram"
        # print "  Sel(=%d) : %3.8f" % (value, a_estimator.estimate_equal(value))
        # print "  Sel(>%d) : %3.8f" % (value, a_estimator.estimate_greater(value))
        # print "Distribution Steps"
        # print "  Sel(=%d) : %3.8f" % (value, b_estimator.estimate_equal(value))
        # print "  Sel(>%d) : %3.8f" % (value, b_estimator.estimate_greater(value))
        # print "Estimador Grupo"
        # print "  Sel(=%d) : %3.8f" % (value, c_estimator.estimate_equal(value))
        # print "  Sel(>%d) : %3.8f" % (value, c_estimator.estimate_greater(value))
        # print "Real"
        # print "  Sel(=%d) : %3.8f" % (value, d_estimator.estimate_equal(value))
        # print "  Sel(>%d) : %3.8f" % (value, d_estimator.estimate_greater(value))
        ea = a_estimator.estimate_equal(value)
        eb = b_estimator.estimate_equal(value)
        ec = c_estimator.estimate_equal(value)
        ed = d_estimator.estimate_equal(value)

        error_a_eq += abs(ea - ed)
        error_b_eq += abs(eb - ed)
        error_c_eq += abs(ec - ed)

        ga = a_estimator.estimate_greater(value)
        gb = b_estimator.estimate_greater(value)
        gc = c_estimator.estimate_greater(value)
        gd = d_estimator.estimate_greater(value)

        error_a_gt += abs(ga - gd)
        error_b_gt += abs(gb - gd)
        error_c_gt += abs(gc - gd)

    print "Classic Histogram"
    print "  Eq error : %3.8f" % (error_a_eq)
    print "  Gt error : %3.8f" % (error_a_gt)
    print "Distribution Steps"
    print "  Eq error : %3.8f" % (error_b_eq)
    print "  Gt error : %3.8f" % (error_b_gt)
    print "Estimador Grupo"
    print "  Eq error : %3.8f" % (error_c_eq)
    print "  Gt error : %3.8f" % (error_c_gt)

test_estimators(50, 'c1')

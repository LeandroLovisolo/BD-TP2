# -*- coding: utf-8 -*-

import estimators

# Creo una instancia de la clase que representa al metodo
# 'Histograma Clasico'
aEstimator = estimators.ClassicHistogram('db.sqlite3', 'table1', 'c1', parameter=20)
bEstimator = estimators.DistributionSteps('db.sqlite3', 'table1', 'c1', parameter=20)
cEstimator = estimators.EstimadorGrupo('db.sqlite3', 'table1', 'c1', parameter=20)
dEstimator = estimators.GroundTruth('db.sqlite3', 'table1', 'c1', parameter=20)

# Pruebo distintas instancias de estimacion
print "Classic Histogram"
print "  Sel(=%d) : %3.8f" % (50, aEstimator.estimate_equal(50))
print "  Sel(>%d) : %3.8f" % (70, aEstimator.estimate_greater(70))
print "Distribution Steps"
print "  Sel(=%d) : %3.8f" % (50, bEstimator.estimate_equal(50))
print "  Sel(>%d) : %3.8f" % (70, bEstimator.estimate_greater(70))
print "Estimador Grupo"
print "  Sel(=%d) : %3.8f" % (50, cEstimator.estimate_equal(50))
print "  Sel(>%d) : %3.8f" % (70, cEstimator.estimate_greater(70))
print "Real"
print "  Sel(=%d) : %3.8f" % (50, dEstimator.estimate_equal(50))
print "  Sel(>%d) : %3.8f" % (70, dEstimator.estimate_greater(70))

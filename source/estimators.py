# -*- coding: utf-8 -*-

import sqlite3
# import numpy as np
# import pylab
# import random

TABLE_NAME = 'table1'


class Estimator(object):
    """Clase base de los estimadores."""

    def __init__(self, db, table, column, parameter=10):
        self.db = db
        self.table = table
        self.column = column
        self.parameter = parameter

        # Construye las estructuras necesita el estimador.
        self.build_struct()

    def build_struct(self):
        raise NotImplementedError()

    def estimate_equal(self, value):
        raise NotImplementedError()

    def estimate_greater(self, value):
        raise NotImplementedError()

    def connect(self):
        self.conn = sqlite3.connect(self.db)


class ClassicHistogram(Estimator):
    def build_struct(self):
        self.eq_histogram = [0 for i in xrange(self.parameter + 1)]
        self.gt_histogram = [0 for i in xrange(self.parameter + 1)]

        self.connect()
        # buscar minimo y maximo y ver de que valor a que valor va el intervalo?
        #   o directamente sobre el rango?

        c = self.conn.cursor()
        self.total = 0

        for row in c.execute('SELECT count(*) FROM %s' % (TABLE_NAME, )):
            value = row[0]
            self.total = value

        first = True

        c = self.conn.cursor()
        for row in c.execute('SELECT %s FROM %s ORDER BY %s ASC' % (self.column, TABLE_NAME, self.column)):
            value = row[0]
            self.max_val = value
            if first:
                self.min_val = value
                first = False

        val_range = self.max_val - self.min_val

        self.bucket_width = int(val_range / self.parameter)  # cantidad de valores que representa una columna del histo

        #   recorrer la base y contar cuantos entran en cada columna
        c = self.conn.cursor()
        for row in c.execute('SELECT %s FROM %s ORDER BY %s ASC' % (self.column, TABLE_NAME, self.column)):
            value = row[0]
            columns = self.get_columns_for(value)
            self.eq_histogram[columns[0]] += 1
            for i in xrange(columns[0]):
                self.gt_histogram[i] += 1

    def estimate_equal(self, value):
        columns = self.get_columns_for(value)
        return float((self.eq_histogram[columns[0]] / self.bucket_width))

    def estimate_greater(self, value):
        columns = self.get_columns_for(value)
        if len(columns) == 1:
            return self.gt_histogram[columns[0]]
        else:
            return float((self.gt_histogram[columns[0]] + self.gt_histogram[columns[1]]) / 2)

    def get_columns_for(self, value):
        # si es exactamente min + bucket_width * k va a ser una sola, sino 2 y promedio los valores
        if value % self.bucket_width == 0 or value == self.max_val:
            return [int((value - self.min_val) / self.bucket_width)]
        else:
            return [int((value - self.min_val) / self.bucket_width),
                    int((value - self.min_val) / self.bucket_width) + 1]


class DistributionSteps(Estimator):
    def build_struct(self):
        self.histogram = [0 for i in xrange(self.parameter + 1)]

        self.connect()

        c = self.conn.cursor()
        self.total = 0

        for row in c.execute('SELECT count(*) FROM %s' % (TABLE_NAME, )):
            value = row[0]
            self.total = value

        items_per_bucket = int(self.total / self.parameter)

        #   recorrer la base y meter items_per_bucket en cada columna
        c = self.conn.cursor()
        items_in_current_bucket = 0
        current_bucket = 0
        value = 0   #fix choto
        for row in c.execute('SELECT %s FROM %s ORDER BY %s ASC' % (self.column, TABLE_NAME, self.column)):
            value = row[0]
            if current_bucket == 0 and items_in_current_bucket == 0:
                self.histogram[current_bucket] = value

            if items_in_current_bucket == items_per_bucket:
                current_bucket += 1
                items_in_current_bucket = 0
                self.histogram[current_bucket] = value

            items_in_current_bucket += 1
        current_bucket += 1
        self.histogram[current_bucket] = value
        print 'end'

    def estimate_equal(self, value):
        if value < self.histogram[0]:
            return 0
        if value > self.histogram[self.parameter]:
            return 0

        for bucket in xrange(self.parameter+1):
            if self.histogram[bucket] > value:
                #CASE A: between steps
                return 1.0 / (3 * self.parameter)
            elif self.histogram[bucket] == value:
                #CASE B/C: equal to steps
                if 0 < bucket < self.parameter and self.histogram[bucket+1] != value:
                    #CASE B1: equal to ONE step and it's NOT FIRST OR LAST
                    return 1.0 / self.parameter
                else:
                    k = 0
                    while self.histogram[bucket+k+1] == value:
                        k += 1
                    if 0 < bucket and self.histogram[self.parameter] != value:
                        #CASE B2: equal to SEVERAL steps, but NOT FIRST OR LAST
                        return float(k / self.parameter)
                    else:
                        #CASE C: equal to ONE OR SEVERAL STEPS including FIRST OR LAST
                        return float((k - 0.5) / self.parameter)

    def estimate_lower(self, value):
        if value < self.histogram[0]:
            return 0
        if value > self.histogram[self.parameter]:
            return self.total

        for bucket in xrange(self.parameter+1):
            if self.histogram[bucket] > value:
                #CASE A: between steps
                return (bucket + 1/3) / self.parameter
            elif self.histogram[bucket] == value:
                #CASE B/C: equal to steps
                if 0 < bucket < self.parameter and self.histogram[bucket+1] != value:
                    #CASE B1: equal to ONE step and it's NOT FIRST OR LAST
                    return (bucket - 0.5) / self.parameter
                else:
                    k = 0
                    while self.histogram[bucket+k+1] == value:
                        k += 1
                    if 0 < bucket and self.histogram[self.parameter] != value:
                        #CASE B2: equal to SEVERAL steps, but NOT FIRST OR LAST
                        return (bucket - 0.5) / self.parameter
                    else:
                        #CASE C: equal to ONE OR SEVERAL STEPS including FIRST OR LAST
                        return 1 - (k - 0.5) / self.parameter

    def estimate_greater(self, value):
        return self.total - self.estimate_equal(value) - self.estimate_lower(value)


class EstimadorGrupo(Estimator):
    def build_struct(self):
        pass

    def estimate_equal(self, value):
        pass

    def estimate_greater(self, value):
        pass
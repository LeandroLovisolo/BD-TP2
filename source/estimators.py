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
        self.eq_histogram = [0 for i in xrange(self.parameter+1)]
        self.gt_histogram = [0 for i in xrange(self.parameter+1)]

        self.connect()
    #   buscar minimo y maximo y ver de que valor a que valor va el intervalo?
    #   o directamente sobre el rango?

        first = True

        c = self.conn.cursor()
        for row in c.execute('SELECT %s FROM %s ORDER BY %s ASC' % (self.column, TABLE_NAME, self.column)):
            value = row[0]
            self.max_val = value
            if first:
                self.min_val = value
                first = False

        val_range = self.max_val - self.min_val

        self.bucket_width = int(val_range/self.parameter)   # cantidad de valores que representa una columna del histo

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
        return self.eq_histogram[columns[0]] / self.bucket_width

    def estimate_greater(self, value):
        columns = self.get_columns_for(value)
        if len(columns) == 1:
            return self.gt_histogram[columns[0]]
        else:
            return (self.gt_histogram[columns[0]] + self.gt_histogram[columns[1]]) / 2

    def get_columns_for(self, value):
        #si es exactamente min + bucket_width * k va a ser una sola, sino 2 y promedio los valores
        if value % self.bucket_width == 0 or value == self.max_val:
            return [int((value-self.min_val) / self.bucket_width)]
        else:
            return [int((value-self.min_val) / self.bucket_width), int((value-self.min_val) / self.bucket_width)+1]


class DistributionSteps(Estimator):

    def build_struct(self):
        pass

    def estimate_equal(self, value):
        pass

    def estimate_greater(self, value):
        pass


class EstimadorGrupo(Estimator):

    def build_struct(self):
        pass

    def estimate_equal(self, value):
        pass

    def estimate_greater(self, value):
        pass
# coding: utf-8

import sqlite3
import numpy as np

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
        self.num_buckets = self.parameter

        self.connect()
        self.compute_range()
        self.compute_bucket_ranges()
        self.compute_buckets()

    def compute_range(self):
        c = self.conn.cursor()
        c.execute('SELECT COUNT(*), MIN(%s), MAX(%s) FROM %s' %
                  (self.column, self.column, self.table))
        row = c.fetchone()
        self.total = int(row[0])
        self.min   = int(row[1])
        self.max   = int(row[2])
        self.step = (self.max - self.min) / self.num_buckets

    def compute_bucket_ranges(self):
        self.buckets = [0 for i in range(0, self.num_buckets)]
        self.bucket_ranges = [None for i in range(0, self.num_buckets)]

        for i in range(0, self.num_buckets):
            bucket_min = self.min + self.step * i
            if i == self.num_buckets - 1: bucket_max = self.max
            else: bucket_max = self.min + self.step * (i + 1) - 1
            self.bucket_ranges[i] = (bucket_min, bucket_max)

    def compute_buckets(self):
        c = self.conn.cursor()
        for i in range(0, self.num_buckets):
            c.execute('''SELECT COUNT(*) FROM %s
                          WHERE %s >= %d
                            AND %s <= %d''' % (self.table,
                                               self.column,
                                               self.bucket_ranges[i][0],
                                               self.column,
                                               self.bucket_ranges[i][1]))
            row = c.fetchone()
            self.buckets[i] = row[0]

    def bucket_for(self, value):
        for i in range(0, len(self.buckets)):
            if self.bucket_ranges[i][0] <= value and value <= self.bucket_ranges[i][1]:
                return i
        return -1

    def estimate_equal(self, value):
        return float(self.buckets[self.bucket_for(value)] / float(self.step)) / self.total

    def estimate_greater(self, value):
        bucket = self.bucket_for(value)
        greater = float(self.buckets[bucket]) / 2
        for i in range(bucket + 1, len(self.buckets)):
            greater += self.buckets[i]
        return greater / self.total

class DistributionSteps(Estimator):
    def build_struct(self):
        self.num_steps = self.parameter
        self.steps = [0] * (self.num_steps + 1)

        self.connect()
        c = self.conn.cursor()

        c.execute('SELECT COUNT(*) FROM %s' % self.table)
        self.total = c.fetchone()[0]

        self.items_per_step = int(np.ceil(float(self.total) / self.num_steps))

        c.execute('SELECT %s FROM %s ORDER BY %s ASC' % (self.column, self.table, self.column))

        for current_step in range(1, self.num_steps + 1):
            if current_step == self.num_steps:
                rows = c.fetchall()
            else:
                rows = c.fetchmany(self.items_per_step)
            if current_step == 1:
                self.steps[0] = rows[0][0]
            self.steps[current_step] = rows[-1][0]

    def estimate_equal(self, value):
        if value < self.steps[0]:
            return 0
        if value > self.steps[self.num_steps]:
            return 0

        for step in xrange(self.num_steps + 1):
            if self.steps[step] > value:
                # CASE A: between steps
                return 1.0 / (3 * self.num_steps)
            elif self.steps[step] == value:
                # CASE B/C: equal to steps
                if 0 < step < self.num_steps and self.steps[step + 1] != value:
                    # CASE B1: equal to ONE step and it's NOT FIRST OR LAST
                    return 1.0 / self.num_steps
                else:
                    k = 0
                    while self.steps[step + k + 1] == value:
                        k += 1
                    if 0 < step and self.steps[self.num_steps] != value:
                        # CASE B2: equal to SEVERAL steps, but NOT FIRST OR LAST
                        return float(k) / self.num_steps
                    else:
                        # CASE C: equal to ONE OR SEVERAL STEPS including FIRST OR LAST
                        return float((k - 0.5) / self.num_steps)

    def estimate_lower(self, value):
        if value < self.steps[0]:
            return 0
        if value > self.steps[self.num_steps]:
            return self.total

        for step in xrange(self.num_steps + 1):

            if self.steps[step] > value:
                # CASE A: between steps
                return (step + 1.0/3) / self.num_steps
            elif self.steps[step] == value:
                # CASE B/C: equal to steps
                if 0 < step < self.num_steps and self.steps[step+1] != value:
                    # CASE B1: equal to ONE step and it's NOT FIRST OR LAST
                    return (step - 0.5) / self.num_steps
                else:
                    k = 0
                    while self.steps[step+k+1] == value:
                        k += 1
                    if 0 < step and self.steps[self.num_steps] != value:
                        # CASE B2: equal to SEVERAL steps, but NOT FIRST OR LAST
                        return (step - 0.5) / self.num_steps
                    else:
                        # CASE C: equal to ONE OR SEVERAL STEPS including FIRST OR LAST
                        return 1 - (k - 0.5) / self.num_steps

    def estimate_greater(self, value):
        return 1 - self.estimate_equal(value) - self.estimate_lower(value)

# noinspection PyArgumentList
class EstimadorGrupo(DistributionSteps):
    def build_struct(self):
        super(EstimadorGrupo, self).build_struct()
        c = self.conn.cursor()
        for row in c.execute('SELECT MAX(%s) FROM %s' % (self.column, self.table)):
            value = row[0]
            self.max_val = value

        c = self.conn.cursor()
        for row in c.execute('SELECT MIN(%s) FROM %s' % (self.column, self.table)):
            value = row[0]
            self.min_val = value

    def range(self):
        return self.max_val - self.min_val

    def estimate_equal(self, value):
        if value < self.steps[0]:
            return 0
        if value > self.steps[self.num_steps]:
            return 0

        for step in xrange(self.num_steps+1):
            if self.steps[step] > value:
                #CASE A: between steps
                return 1.0 / self.range()
            elif self.steps[step] == value:
                #CASE B/C: equal to steps
                if 0 < step < self.num_steps and self.steps[step+1] != value:
                    #CASE B1: equal to ONE step and it's NOT FIRST OR LAST
                    return 1.0 / self.total
                else:
                    k = 0
                    while self.steps[step+k+1] == value:
                        k += 1
                    if 0 < step and self.steps[self.num_steps] != value:
                        #CASE B2: equal to SEVERAL steps, but NOT FIRST OR LAST
                        return float(k) / self.num_steps
                    else:
                        #CASE C: equal to ONE OR SEVERAL STEPS including FIRST OR LAST
                        return float((k - 0.5) / self.num_steps)

    def estimate_lower(self, value):
        if value < self.steps[0]:
            return 0
        if value > self.steps[self.num_steps]:
            return self.total

        for step in xrange(self.num_steps+1):

            if self.steps[step] > value:
                #CASE A: between steps
                return (step + 1.0/2) / self.num_steps - self.estimate_equal(value) / 2
            elif self.steps[step] == value:
                #CASE B/C: equal to steps
                if 0 < step < self.num_steps and self.steps[step+1] != value:
                    #CASE B1: equal to ONE step and it's NOT FIRST OR LAST
                    return float(step) / self.num_steps - self.estimate_equal(value) / 2
                else:
                    k = 0
                    while self.steps[step+k+1] == value:
                        k += 1
                    if 0 < step and self.steps[self.num_steps] != value:
                        #CASE B2: equal to SEVERAL steps, but NOT FIRST OR LAST
                        return float(step) / self.num_steps - self.estimate_equal(value) / 2
                    else:
                        #CASE C: equal to ONE OR SEVERAL STEPS including FIRST OR LAST
                        return 1 - float(k) / self.num_steps - self.estimate_equal(value) / 2

class GroundTruth(Estimator):

    def build_struct(self):
        self.connect()

    def estimate_equal(self, value):
        c = self.conn.cursor()

        c.execute('SELECT COUNT(%s) FROM %s' % (self.column, self.table))
        total = c.fetchone()[0]

        c.execute('SELECT COUNT(%s) FROM %s WHERE %s = %s' % (self.column, self.table, self.column, value))
        count = c.fetchone()[0]

        return float(count) / total

    def estimate_greater(self, value):
        c = self.conn.cursor()

        c.execute('SELECT COUNT(%s) FROM %s' % (self.column, self.table))
        total = c.fetchone()[0]

        c.execute('SELECT COUNT(%s) FROM %s WHERE %s > %s' % (self.column, self.table, self.column, value))
        count = c.fetchone()[0]

        return float(count) / total

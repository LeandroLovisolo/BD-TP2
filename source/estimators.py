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
        self.connect()
        self.compute_range()
        self.compute_bucket_ranges()
        self.compute_buckets()

    def compute_range(self):
        c = self.conn.cursor()
        c.execute('SELECT COUNT(*), MIN(%s), MAX(%s) FROM %s' %
                  (self.column, self.column, self.table))
        row = c.fetchone()

        self.total       = int(row[0])
        self.min         = int(row[1])
        self.max         = int(row[2])
        self.num_buckets = min(self.parameter, self.max - self.min + 1)
        self.step        = float(self.max - self.min) / self.num_buckets

    def compute_bucket_ranges(self):
        self.buckets = [0 for i in range(0, self.num_buckets)]

        self.bucket_ranges = []
        for i in range(0, self.num_buckets):
            low  = self.min + int(self.step * i)
            high = self.min + int(self.step * (i + 1)) - 1
            if i == self.num_buckets - 1:
                high = self.max
            self.bucket_ranges.append((low, high))

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
        if value > self.max or value < self.min:
            return 0
        return float(self.buckets[self.bucket_for(value)] / self.step) / self.total

    def estimate_greater(self, value):
        #print 'Se llama a estimate_greater con value: ' + str(value) + ' maximo: ' + str(self.max) + ' min: ' + str(self.min)
        if value > self.max:
            print 'Valor por arriba de max'
            return 0
        elif value < self.min:
            print 'Valor por debajo de min'
            return 1

        bucket = self.bucket_for(value)
        #print 'Bucket numero: ' + str(bucket)
        #print '[bucket][0]: ' + str(self.bucket_ranges[bucket][0]) + '[bucket][1]' + str(self.bucket_ranges[bucket][1])
        #print '[bucket][1] - value: ' + str(self.bucket_ranges[bucket][1] - value)
        factor = float(self.bucket_ranges[bucket][1] - value) / self.step
        #print 'Factor: ' + str(factor)
        
        greater = float(self.buckets[bucket]) * factor
        #print 'Greater inicial: ' + str(greater)
        #greater = float(self.buckets[bucket]) / 2
        for i in range(bucket + 1, len(self.buckets)):
            greater += self.buckets[i]
        #print 'Greater: ' + str(greater)
        return greater / self.total - self.estimate_equal(value)

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
                    while len(self.steps) > step + k + 1 and self.steps[step + k + 1] == value:
                        k += 1
                    if 0 < step and self.steps[self.num_steps] != value:
                        # CASE B2: equal to SEVERAL steps, but NOT FIRST OR LAST
                        return float(k) / self.num_steps
                    else:
                        # CASE C: equal to ONE OR SEVERAL STEPS including FIRST OR LAST
                        return float((k - 0.5) / self.num_steps)

    def estimate_lower(self, value):
        if value <= self.steps[0]:
            return 0
        if value > self.steps[self.num_steps]:
            return 1

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
                    while len(self.steps) > step + k + 1 and self.steps[step+k+1] == value:
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
                step_range = self.steps[step] - self.steps[step-1] +1
                return float(self.items_per_step)/ step_range / self.total
                #return 1.0 / self.range()
            elif self.steps[step] == value:
                #CASE B/C: equal to steps
                if 0 < step < self.num_steps and self.steps[step+1] != value:
                    #CASE B1: equal to ONE step and it's NOT FIRST OR LAST
                    return 1.0 / self.total
                else:
                    k = 0
                    while len(self.steps) > step + k + 1 and self.steps[step+k+1] == value:
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
                step_range = self.steps[step] - self.steps[step-1] + 1
                factor = float(value - self.steps[step-1]) / step_range
                return (step + factor) / self.num_steps - self.estimate_equal(value) / 2
                # return (step + 1.0/2) / self.num_steps - self.estimate_equal(value) / 2
            elif self.steps[step] == value:
                #CASE B/C: equal to steps
                if 0 < step < self.num_steps and self.steps[step+1] != value:
                    #CASE B1: equal to ONE step and it's NOT FIRST OR LAST
                    return float(step) / self.num_steps - self.estimate_equal(value) / 2
                else:
                    k = 0
                    while len(self.steps) > step + k + 1 and self.steps[step+k+1] == value:
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

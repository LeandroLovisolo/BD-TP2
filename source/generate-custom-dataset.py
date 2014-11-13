#!/usr/bin/env python2

import sqlite3
import numpy as np

NUM_TUPLES   = 100000

UNIFORM_LOW  = 0
UNIFORM_HIGH = 100

NORMAL_MEAN  = 100
NORMAL_STD   = 50

if __name__ == '__main__':
    print "Creating dataset..."

    conn = sqlite3.connect('custom.sqlite3')
    c = conn.cursor()

    c.execute('DROP TABLE IF EXISTS data')
    c.execute('CREATE TABLE data (uniform INTEGER, normal INTEGER)')

    uniform = np.random.uniform(low=UNIFORM_LOW, high=UNIFORM_HIGH, size=NUM_TUPLES)
    normal  = np.random.normal(loc=NORMAL_MEAN, scale=NORMAL_STD, size=NUM_TUPLES)

    for tuple in zip(uniform, normal):
        c.execute('INSERT INTO data VALUES (?, ?)', tuple)

    conn.commit()
    conn.close()

    print "Done."

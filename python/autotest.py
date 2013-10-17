
import os
import glob
import subprocess
import random
import unittest
import time
import numpy as np
import sys
import readingdb as rdb

# make sure we're testing the version of readingdb in this dir.
assert os.path.dirname(os.path.abspath(rdb.__file__)) == \
    os.path.dirname(os.path.abspath(__file__))

datadir = '_testdata'
readingdb = '../src/reading-server'
log = "afile"
port = int(random.random() * 5000) + 20000

class TestIface(unittest.TestCase):
    def setUp(self):
        
        if False:
            try:
                os.makedirs(datadir)
            except OSError, e:
                if e.errno != os.errno.EEXIST:
                    raise
            cmd = [readingdb, '-p', str(port), '-d', datadir, '-c', '1']
            self.log = open(log, 'a')
            self.db = subprocess.Popen(cmd, stderr=sys.stderr, stdout=sys.stderr)

            # wait for startup or a fatal message
            for x in xrange(0, 50):
                l = self.db.stderr.readline()
                print "l was: ",l
                if 'FATAL' in l:
                    raise Exception(l)
                elif 'listening' in l:
                    break
            print "starting conn open"
        self.conn = rdb.db_open('localhost', 4242)

    def tearDown(self):
        rdb.db_close(self.conn)
        #self.db.terminate()
        #self.db.wait()
        #self.log.close()

        #for f in glob.glob(os.path.join(datadir, '*')):
        #    os.remove(f)
        #os.removedirs(datadir)

    def infill_stream(self, stream):
        for i in range(0, 1000):
            data = [(x, x, x) for x in xrange(i * 100, i * 100 + 100)]
            self.assertEqual(rdb.db_add(self.conn, stream, data), 1)


    def test_simple(self):
        self.infill_stream(1)
        d = rdb.db_query([1], 0, 10000, conn=self.conn)[0]
        self.assertEqual(len(d[0]), 10000)
        self.assertEqual(len(d[1]), 10000)
        for i in xrange(0, 10000):
            self.assertEqual(d[0][i], i)
            self.assertEqual(d[1][i], i)

    def test_multi(self):
        streams = range(1, int(1e4), int(1e3))
        for i in streams:
            self.infill_stream(i)

        rdb.db_setup('localhost', port)
        fetch = random.sample(streams, 3)
        data = rdb.db_query(fetch, 0, 10000, conn=self.conn)

        # check grabbing three random streams
        self.assertEqual(len(data), 3)
        for dv in data:
            self.assertEqual(dv[0].shape, (10000,))
            self.assertEqual(dv[1].shape, (10000,))
            self.assertEqual(np.sum(dv[0] - np.arange(0, 10000)), 0)
            self.assertEqual(np.sum(dv[1] - np.arange(0, 10000)), 0)

        # grab some streams without data
        data = rdb.db_query([2,3,4,6], 0, 10000, conn=self.conn)
        self.assertEqual(len(data), 4)
        for dv in data:
            self.assertEqual(dv[0].shape, (0,))
            self.assertEqual(dv[1].shape, (0,))


if __name__ == '__main__':
    unittest.main()

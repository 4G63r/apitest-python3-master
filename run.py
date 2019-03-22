import unittest
from tests import APITest
from base import HTMLTestReportCN

import time

suite = unittest.TestSuite()

suite.addTest(APITest('test_01'))
suite.addTest(APITest('test_02'))

now = time.strftime('%Y%m%d_%H%M%S')
with open('./report/%s.html' % now, 'wb') as f:
    # with open('./report/index.html', 'wb') as f:
    HTMLTestReportCN.HTMLTestRunner(stream=f, title='接口自动化报告', verbosity=2).run(suite)

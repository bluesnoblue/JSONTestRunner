from unittest import defaultTestLoader, TextTestRunner
from JSONTestRunner import JSONTestRunner
from time import strftime
import os

cases = defaultTestLoader.discover('./cases/', pattern='test*.py')
# runner = TextTestRunner()
time_string = strftime('%Y-%m-%d_%H-%M-%S')
if not os.path.exists('reports'):
    os.mkdir('reports')
with open(f'./reports/report_{time_string}.json', 'w') as fp:
    runner = JSONTestRunner(stream=fp)
    result = runner.run(cases)
    # print(result)

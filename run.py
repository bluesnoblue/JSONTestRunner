from unittest import defaultTestLoader, TextTestRunner
from JSONTestRunner import JSONTestRunner
from time import strftime

cases = defaultTestLoader.discover('./cases/', pattern='test*.py')
# runner = TextTestRunner()
time_string = strftime('%Y-%m-%d_%H-%M-%S')
with open(f'./reports/report_{time_string}.json', 'w') as fp:
    runner = JSONTestRunner(stream=fp)
    result = runner.run(cases)
    # print(result)

from unittest import defaultTestLoader
from JSONTestRunner import JSONTestRunner
import requests

cases = defaultTestLoader.discover('demo-cases/', pattern='test*.py')
runner = JSONTestRunner()
reprot = runner.run(cases)
r = requests.post('http://127.0.0.1:5000/reports', json=reprot)
print(r.status_code)

import datetime
import io
import unittest
import sys
import json


class OutputRedirector(object):
    """ Wrapper to redirect stdout or stderr """

    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()


stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)
TestResult = unittest.TestResult


class _TestResult(TestResult):

    def __init__(self, verbosity=1):
        super().__init__(self)
        self.stdout0 = None
        self.stderr0 = None
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.verbosity = verbosity
        # result is a list of result in 4 tuple
        # (
        #   result code (0: success; 1: fail; 2: error),
        #   TestCase object,
        #   Test output (byte string),
        #   stack trace,
        # )
        self.result = []
        self.passrate = float(0)

    def startTest(self, test):
        TestResult.startTest(self, test)
        # just one buffer for both stdout and stderr
        self.outputBuffer = io.StringIO()
        stdout_redirector.fp = self.outputBuffer
        stderr_redirector.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def complete_output(self):
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()

    def addSuccess(self, test):
        self.success_count += 1
        TestResult.addSuccess(self, test)
        output = self.complete_output()
        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stderr.write('ok ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('.')

    def addError(self, test, err):
        self.error_count += 1
        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('E  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E')

    def addFailure(self, test, err):
        self.failure_count += 1
        TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('F  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('F')


class JSONTestRunner:
    STATUS = {
        0: '通过',
        1: '失败',
        2: '错误',
    }

    def __init__(self, stream=sys.stdout, verbosity=1, title='测试报告', description='', tester='tester'):
        self.stream = stream
        self.verbosity = verbosity
        self.title = title
        self.description = description
        self.tester = tester
        self.start_time = datetime.datetime.now()
        self.stop_time = None
        self.pass_rate = None

    def run(self, test):
        result = _TestResult(self.verbosity)
        test(result)
        self.stop_time = datetime.datetime.now()
        self.generate_report(result)
        return result

    def generate_report(self, result):
        report_attrs = self.get_report_attributes(result)
        report = self._generate_report(result)
        output = dict(attributes=report_attrs, report=report)
        j = json.dumps(output,indent=2)
        self.stream.write(j)

    def _generate_report(self, result):
        rows = []
        sorted_result = self.sort_result(result.result)
        for cid, (cls, cls_results) in enumerate(sorted_result):
            # subtotal for a class

            np = nf = ne = 0
            for n, t, o, e in cls_results:
                if n == 0:
                    np += 1
                elif n == 1:
                    nf += 1
                else:
                    ne += 1
            # format class description
            if cls.__module__ == "__main__":
                name = cls.__name__
            else:
                name = "%s.%s" % (cls.__module__, cls.__name__)
            doc = cls.__doc__ and cls.__doc__.split("\n")[0] or ""
            desc = doc and '%s: %s' % (name, doc) or name

            # row = f'{ne},{desc},{np + nf + ne},{np},{nf},{ne},{cid + 1}'
            test_list = []
            for tid, (n, t, o, e) in enumerate(cls_results):
                test_list.append(self._generate_report_test(cid, tid, n, t, o, e))

            row = dict(desc=desc, count=np + nf + ne, Pass=np, fail=nf, error=ne, id=cid + 1, test_list=test_list)
            rows.append(row)

        report = dict(
            test_list=rows,
            count=str(result.success_count + result.failure_count + result.error_count),
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
            pass_rate=self.pass_rate,
        )
        # report = f'{report}'

        return report

    def _generate_report_test(self, cid, tid, n, t, o, e):
        has_output = bool(o or e)
        tid = (n == 0 and 'p' or 'f') + 't%s_%s' % (cid + 1, tid + 1)
        name = t.id().split('.')[-1]
        doc = t.shortDescription() or ""
        desc = doc and ('%s: %s' % (name, doc)) or name
        # o and e should be byte string because they are collected from stdout and stderr?
        if isinstance(o, str):
            # uo = unicode(o.encode('string_escape'))
            # uo = o.decode('latin-1')
            uo = o
        else:
            uo = o
        if isinstance(e, str):
            # ue = unicode(e.encode('string_escape'))
            # ue = e.decode('latin-1')
            ue = e
        else:
            ue = e

        # 一个方法的结果
        report_test = dict(
            tid=tid,
            Class=(n == 0 and 'hiddenRow' or 'none'),
            style=n == 2 and 'errorCase' or (n == 1 and 'failCase' or 'passCase'),
            desc=desc,
            # status=self.STATUS[n],
            status=n,
            ue=ue,
            uo=uo
        )
        # row = f'{row}'
        return report_test

    @staticmethod
    def sort_result(result_list):
        # unittest does not seems to run in any particular order.
        # Here at least we want to group them together by class.
        rmap = {}
        classes = []
        for n, t, o, e in result_list:
            cls = t.__class__
            if cls not in rmap:
                rmap[cls] = []
                classes.append(cls)
            rmap[cls].append((n, t, o, e))
        r = [(cls, rmap[cls]) for cls in classes]
        return r

    def get_report_attributes(self, result):
        start_time = str(self.start_time)[:19]
        duration = str(self.stop_time - self.start_time)
        # status = list()
        # total = result.success_count + result.failure_count + result.error_count
        # status.append(f'total: {total}')
        # if result.success_count:
        #     status.append(f'PASS: {result.success_count}')
        # if result.failure_count:
        #     status.append(f'FAILED: {result.failure_count}')
        # if result.error_count:
        #     status.append(f'ERROR: {result.error_count}')
        # if status:
        #     if result.success_count + result.failure_count + result.error_count:
        #         self.pass_rate = str("%.2f%%" % (float(result.success_count) / float(
        #             result.success_count + result.failure_count + result.error_count) * 100))
        #     else:
        #         self.pass_rate = 'N/A'
        # else:
        #     status = 'none'
        report_attributes = dict(
            tester=self.tester,
            start_time=start_time,
            duration=duration,
            # status=status,
            # pass_rate=self.pass_rate
        )
        return report_attributes

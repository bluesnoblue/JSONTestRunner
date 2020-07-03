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
        self.pass_rate = float(0)
        self.outputBuffer = None

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

    def __init__(self, stream=sys.stdout, verbosity=1, title='测试报告', description='', tester='测试人员'):
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
        attributes = self._get_report_attributes()
        result_ = self._generate_result(result)

        report = dict(attributes=attributes, result=result_)
        report = json.dumps(report, indent=2)
        self.stream.write(report)

    def _get_report_attributes(self):
        start_time = str(self.start_time)[:19]
        duration = str(self.stop_time - self.start_time)

        report_attributes = dict(
            title=self.title,
            tester=self.tester,
            description=self.description,
            start_time=start_time,
            duration=duration
        )
        return report_attributes

    def _generate_result(self, result):
        sorted_result = self.sort_result(result.result)
        case_results = self._generate_class_result(sorted_result)
        # 计算通过率
        total = result.success_count + result.failure_count + result.error_count
        self.pass_rate = total and str("%.2f%%" % (float(result.success_count) / float(total) * 100)) or 'No Test'

        result_ = dict(
            count=str(result.success_count + result.failure_count + result.error_count),
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
            pass_rate=self.pass_rate,
            case_results=case_results,
        )
        return result_

    def _generate_class_result(self, result):
        case_results = []
        for cls_id, (cls, cls_results) in enumerate(result):
            # 类中的统计
            num_pass = num_fail = num_error = 0
            for n, _, _, _ in cls_results:
                if n == 0:
                    num_pass += 1
                elif n == 1:
                    num_fail += 1
                else:
                    num_error += 1
            count = num_pass + num_fail + num_error
            # 获取类名（模块+类名）
            if cls.__module__ == "__main__":
                name = cls.__name__
            else:
                name = "%s.%s" % (cls.__module__, cls.__name__)
            # 获取类中的doc
            doc = cls.__doc__ and cls.__doc__.split("\n")[0] or ""
            # 获取类中测试方法的结果
            method_results = self._generate_method_result(cls_id, cls_results)

            case_result = dict(
                id=cls_id + 1,
                name=name,
                doc=doc,
                count=count,
                Pass=num_pass,
                fail=num_fail,
                error=num_error,
                method_results=method_results
            )
            case_results.append(case_result)

        return case_results

    def _generate_method_result(self, cls_id, cls_results):
        method_results = []
        for method_id, (n, method, output, error) in enumerate(cls_results):
            tid = (n == 0 and 'p' or 'f') + 't%s_%s' % (cls_id + 1, method_id + 1)  # todo： 这里的tid规则很奇怪
            name = method.id().split('.')[-1]
            doc = method.shortDescription() or ""
            # 一个方法的结果
            # todo：渲染相关的参数不应该放在raw数据中
            method_result = dict(
                id=tid,
                name=name,
                doc=doc,
                status=self.STATUS[n],
                # status=n,
                error=error,
                output=output,
                Class=(n == 0 and 'hiddenRow' or 'none'),  # view渲染相关
                style=n == 2 and 'errorCase' or (n == 1 and 'failCase' or 'passCase'),  # view渲染相关
                button_type=n == 0 and 'btn-success' or (n == 1 and 'btn-danger' or 'btn-warning')
            )
            method_results.append(method_result)
        return method_results

    @staticmethod
    def sort_result(result_list):
        # unittest does not seems to run in any particular order.
        # Here at least we want to group them together by class.
        rmap = {}
        classes = []
        for n, test_method, output, error in result_list:
            cls = test_method.__class__
            if cls not in rmap:
                rmap[cls] = []
                classes.append(cls)
            rmap[cls].append((n, test_method, output, error))
        r = [(cls, rmap[cls]) for cls in classes]
        return r

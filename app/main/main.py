def get_report_together(report_list):
    report_num = len(report_list)
    all_test_method = dict()
    for report in report_list:
        for case_result in report['case_results']:
            class_name = case_result['name']
            for method in case_result['method_results']:
                test_method = f'{class_name}.{method["name"]}'
                if test_method not in all_test_method:
                    all_test_method[test_method] = ['未执行'] * report_num

    for index_of_report_list in range(report_num):
        report = report_list[index_of_report_list]
        for case_results in report['case_results']:
            class_name = case_results['name']
            for method in case_results['method_results']:
                test_method = f'{class_name}.{method["name"]}'
                all_test_method[test_method][index_of_report_list] = method['status']
    return all_test_method


def cul_rate(report):
    pass_ = int(report['Pass'])
    fail = int(report['fail'])
    error = int(report['error'])
    total = pass_ + fail + error
    fail_rate = total and str("%.0f%%" % (float(fail) / float(total) * 100)) or '0%'
    error_rate = total and str("%.0f%%" % (float(error) / float(total) * 100)) or '0%'
    pass_rate = f'{100 - int(fail_rate.split("%")[0]) - int(error_rate.split("%")[0])}%'
    report_ = dict(
        Pass_num=pass_,
        fail_num=fail,
        error_num=error,
        Pass=report['Pass'],
        fail_rate=fail_rate,
        error_rate=error_rate,
        Pass_rate=pass_rate
    )
    report.update(report_)


def check_report(report):
    keys = ['title', 'tester', 'start_time', 'duration', 'count', 'pass_rate', 'Pass', 'fail', 'error', 'case_results']
    for key in keys:
        assert key in report

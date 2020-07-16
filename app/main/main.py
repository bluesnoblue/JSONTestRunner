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

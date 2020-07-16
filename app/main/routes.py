from app.main import bp
from .main import get_report_together
from flask import render_template
import os
import json


@bp.route('/', methods=['GET'])
def home():
    files = []
    reports = []

    for file in os.listdir('./reports'):
        file_name, suffix = file.split('.')
        if suffix == 'json':
            files.append(file_name)
    files.sort(reverse=True)

    for file in files[:5]:
        with open(f'./reports/{file}.json') as fp:
            report = json.load(fp)
            pass_ = int(report['Pass'])
            fail = int(report['fail'])
            error = int(report['error'])
            total = pass_ + fail + error
            fail_rate = total and str("%.0f%%" % (float(fail) / float(total) * 100)) or '0%'
            error_rate = total and str("%.0f%%" % (float(error) / float(total) * 100)) or '0%'
            pass_rate = f'{100 - int(fail_rate.split("%")[0]) - int(error_rate.split("%")[0])}%'
            report_ = dict(
                file_name=file,
                Pass_num=pass_,
                fail_num=fail,
                error_num=error,
                fail_rate=fail_rate,
                error_rate=error_rate,
                Pass_rate=pass_rate
            )
            report_.update(report)
            reports.append(report_)
    return render_template('overview_page.html', title='OverView', reports=reports, report=reports[0])


@bp.route('/reports', methods=['GET'])
def report_list():
    files = []
    reports = []

    for file in os.listdir('./reports'):
        file_name, suffix = file.split('.')
        if suffix == 'json':
            files.append(file_name)
    files.sort(reverse=True)
    for file in files:
        with open(f'./reports/{file}.json') as fp:
            report = json.load(fp)
            pass_ = int(report['Pass'])
            fail = int(report['fail'])
            error = int(report['error'])
            total = pass_ + fail + error
            fail_rate = total and str("%.0f%%" % (float(fail) / float(total) * 100)) or '0%'
            error_rate = total and str("%.0f%%" % (float(error) / float(total) * 100)) or '0%'
            pass_rate = f'{100 - int(fail_rate.split("%")[0]) - int(error_rate.split("%")[0])}%'
            report_ = dict(
                file_name=file,
                Pass_num=pass_,
                fail_num=fail,
                error_num=error,
                Pass=report['Pass'],
                fail_rate=fail_rate,
                error_rate=error_rate,
                Pass_rate=pass_rate
            )
            report_.update(report)
            reports.append(report_)
    return render_template('report_list_page.html', title='Report List', reports=reports)


@bp.route('/reports_contrast', methods=['GET'])
def report_contrast():
    files = []
    reports = []

    for file in os.listdir('./reports'):
        file_name, suffix = file.split('.')
        if suffix == 'json':
            files.append(file_name)
    files.sort(reverse=False)

    some_file = files[-3:]
    for file in some_file:
        with open(f'./reports/{file}.json') as fp:
            report = json.load(fp)
            reports.append(report)

    data = get_report_together(reports)
    return render_template('contrast_page.html', title='Contrast Detail', data=data, files=some_file)


@bp.route('/reports/<reports_name>', methods=['GET'])
def report_detail(reports_name):
    # todo: 需要判断文件是否存在
    with open(f'./reports/{reports_name}.json', encoding='utf-8') as fp:
        report = json.load(fp)
    return render_template('detail_page.html', title='Report Detail', report=report)

from app.main import bp
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
            pass_ = int(report['result']['Pass'])
            fail = int(report['result']['fail'])
            error = int(report['result']['error'])
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
                pass_rate=pass_rate
            )
            report_.update(report['attributes'])
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
            pass_ = int(report['result']['Pass'])
            fail = int(report['result']['fail'])
            error = int(report['result']['error'])
            total = pass_ + fail + error
            fail_rate = total and str("%.0f%%" % (float(fail) / float(total) * 100)) or '0%'
            error_rate = total and str("%.0f%%" % (float(error) / float(total) * 100)) or '0%'
            pass_rate = f'{100 - int(fail_rate.split("%")[0]) - int(error_rate.split("%")[0])}%'
            report_ = dict(
                file_name=file,
                Pass_num=pass_,
                fail_num=fail,
                error_num=error,
                Pass=report['result']['Pass'],
                fail_rate=fail_rate,
                error_rate=error_rate,
                pass_rate=pass_rate
            )
            report_.update(report['attributes'])
            reports.append(report_)
    return render_template('report_list_page.html', title='Report List', reports=reports)


@bp.route('/reports/<reports_name>', methods=['GET'])
def report_detail(reports_name):
    # todo: 需要判断文件是否存在
    with open(f'./reports/{reports_name}.json', encoding='utf-8') as fp:
        report = json.load(fp)
    return render_template('detail_page.html', title='Report Detail', report=report)

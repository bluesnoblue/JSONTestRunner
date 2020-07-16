from app.main import bp
from app import mongo
from .main import get_report_together, check_report, cul_rate
from flask import render_template, request, jsonify
from bson import ObjectId


@bp.route('/', methods=['GET'])
def home():
    reports = []
    for report in mongo.db.reports.find().sort('_id', -1).limit(5):
        cul_rate(report)
        reports.append(report)
    return render_template('overview_page.html', title='OverView', reports=reports, report=reports[0])


@bp.route('/reports', methods=['GET', 'POST'])
def report_list():
    if request.method == 'POST':  # 上传报告
        report = request.get_json()
        try:
            check_report(report)
            mongo.db.reports.insert(report)
        except AssertionError:
            return jsonify({'desc': '请求入参有误'}), 499
        return '', 204
    else:
        reports = []
        for report in mongo.db.reports.find().sort('_id', -1):
            cul_rate(report)
            reports.append(report)
        return render_template('report_list_page.html', title='Report List', reports=reports)


@bp.route('/reports_contrast', methods=['GET'])
def report_contrast():
    reports = []
    for report in mongo.db.reports.find().sort('_id', -1).limit(3):
        reports.append(report)
    # 不知道升序的最后3个怎么写sql...
    reports = reports[::-1] # 用 降序的前三个再逆序 来实现 升序的最后3个...
    time_list = [report['start_time'] for report in reports]
    data = get_report_together(reports)
    return render_template('contrast_page.html', title='Contrast Detail', data=data, time_list=time_list)


@bp.route('/reports/<report_id>', methods=['GET'])
def report_detail(report_id):
    # todo: 需要判断文件是否存在
    report = mongo.db.reports.find_one({'_id': ObjectId(report_id)})
    print(report)
    return render_template('detail_page.html', title='Report Detail', report=report)

from app.main import bp
from flask import render_template
import os
import json


@bp.route('/', methods=['GET'])
def home():
    files = []
    for file in os.listdir('./reports'):
        file_name = file.split('.')[0]
        files.append(file_name)
    files.sort(reverse=True)
    return render_template('index.html', title='Home Page', files=files)


@bp.route('/reports/<reports_name>', methods=['GET'])
def report_detail(reports_name):
    with open(f'./reports/{reports_name}.json', encoding='utf-8') as fp:
        report = json.load(fp)
    return render_template('detail.html', title='Detail Page', report=report)

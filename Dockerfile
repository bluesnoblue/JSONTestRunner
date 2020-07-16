FROM python:3.7-alpine
WORKDIR /code
RUN pip install flask -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
RUN pip install flask_bootstrap -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
COPY . .
CMD ["python", "reports_server.py", "-d"]
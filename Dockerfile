FROM python:3.7-alpine
WORKDIR /code
COPY . .
RUN pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
CMD ["python", "reports_server.py", "-d"]
#FROM registry.cn-shanghai.aliyuncs.com/jwh/python:2.7
FROM registry.cn-shanghai.aliyuncs.com/jwh/python:3.10
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
EXPOSE 8000
ENV TZ Asia/Shanghai

CMD ["uwsgi", "uwsgi.ini"]

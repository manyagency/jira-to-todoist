FROM python:3.7-stretch

RUN pip install jira todoist-python gunicorn

ADD ./sync.py /

CMD ["python", "/sync.py"]

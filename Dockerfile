FROM python:3.7-stretch

RUN pip install jira todoist-python gunicorn

ADD ./sync.py /

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 sync:sync

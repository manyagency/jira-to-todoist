FROM python:3.7-stretch

RUN pip install jira todoist-python
EXPOSE 8080
ADD ./sync.py /
CMD ["python", "/sync.py"]

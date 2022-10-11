from time import sleep
from jira import JIRA
from os import getenv
from datetime import datetime
import todoist
import socket

HOST = ''
PORT = getenv('PORT')

JIRA_URL = getenv('JIRA_URL')
JIRA_USERNAME = getenv('JIRA_USERNAME')
JIRA_API_KEY = getenv('JIRA_API_KEY')
JIRA_PROJECT = getenv('JIRA_PROJECT')
TODOIST_TOKEN = getenv('TODOIST_TOKEN')
TODOIST_LABEL = getenv('TODOIST_LABEL')


def get_jira_client():
    jira = JIRA(JIRA_URL, basic_auth=(JIRA_USERNAME, JIRA_API_KEY))
    return jira


def get_jira_tasks(client=None):
    if not client:
        client = get_jira_client()
    keepScanning = True
    issues = []
    max_results = 50
    start_at = 0
    while keepScanning:
        got_issues = client.search_issues(
            "assignee = currentUser() and project IN (\"" + JIRA_PROJECT + "\")", maxResults=max_results, startAt=start_at)
        if len(got_issues) > 0:
            issues = issues + got_issues
            start_at += max_results
        else:
            keepScanning = False
    return issues


def get_todoist_api():
    api = todoist.TodoistAPI(TODOIST_TOKEN)
    api.sync()
    return api


def get_label_with_name(api, name):
    all_labels = api.labels.all()
    this_label = list(
        filter(lambda x: x['name'].lower() == name.lower(), all_labels))[0]
    return this_label


def get_project_with_name(api, name):
    all_labels = api.projects.all()
    this_project = list(
        filter(lambda x: x['name'].lower() == name.lower(), all_labels))[0]
    return this_project


def get_tasks_for_label(api, label_id):
    all_tasks = api.items.all()
    this_label_tasks = list(
        filter(lambda x: label_id in x['labels'], all_tasks))
    return this_label_tasks


def get_tasks_for_project(api, project_id):
    all_tasks = api.items.all()
    this_project_tasks = list(
        filter(lambda x: project_id == x['project_id'], all_tasks))
    return this_project_tasks


def compare_tasks(api, project_id, todoist_tasks, jira_tasks):
    created_items = 0
    for j in jira_tasks:
        todoist_name = "[{}] {}".format(j.key, j.fields.summary)
        possible_todoist_tasks = list(
            filter(lambda x: x['content'] == todoist_name, todoist_tasks))

        if len(possible_todoist_tasks) == 0:
            if j.fields.resolution == None:
                api.items.add(todoist_name, project_id=project_id)
                created_items += 1
                print("adding {}".format(todoist_name))

        else:
            this_todoist_task = possible_todoist_tasks[0]
            if j.fields.resolution != None:

                this_todoist_task.close()
                created_items += 1
                print("completing {}".format(todoist_name))

        if(created_items == 50):
            created_items = 0
            print(api.commit())
            sleep(5)

    if created_items > 0:
        print(api.commit())


def main(label):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.bind(('', 8080))

    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    print('Socket bind complete')

    print("starting sync at {}".format(datetime.now().isoformat()))
    api = get_todoist_api()
    # label = get_label_with_name(api, label)
    project = get_project_with_name(api, label)
    # todoist_tasks = get_tasks_for_label(api, label['id'])
    todoist_tasks = get_tasks_for_project(api, project['id'])

    client = get_jira_client()
    jira_tasks = get_jira_tasks(client)

    compare_tasks(api, project['id'], todoist_tasks, jira_tasks)


if __name__ == "__main__":
    main(TODOIST_LABEL)

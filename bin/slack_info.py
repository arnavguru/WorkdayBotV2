import os
import requests

slack_api_url = 'https://slack.com/api/users.profile.get'
slack_header = {'content-type': 'application/x-www-form-urlencoded'}
slack_oauth = os.environ['SLACK_OAUTH']
slack_post_url = slack_api_url + '?token=' + slack_oauth + '&user='


def get_slack_email(event):
    if event['requestAttributes']['x-amz-lex:channel-type'].__contains__('Slack'):
        slack_user = event['userId'].split(':', 3)[-1]
        slack_response = requests.post(slack_post_url + slack_user, headers=slack_header)
        slack_response = slack_response.json()
        slack_email = slack_response['profile']['email']
        return slack_email
    else:
        return None

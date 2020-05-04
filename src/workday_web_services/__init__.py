import os

headers = {'content-type': 'text/plain; charset=utf-8'}
workday_id = os.environ['WORKDAY_ID']
workday_pwd = os.environ['WORKDAY_PWD']
workday_ws_url = os.environ['WORKDAY_WS_URL']
workday_custom_report_url = os.environ['WORKDAY_CUSTOM_REPORT_URL']
version = os.environ['WORKDAY_VERSION']

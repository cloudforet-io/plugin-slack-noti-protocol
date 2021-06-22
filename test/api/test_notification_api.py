import os
import logging

from spaceone.core import utils, config
from spaceone.tester import TestCase, print_json, to_json
from google.protobuf.json_format import MessageToDict

_LOGGER = logging.getLogger(__name__)

TOKEN = os.environ.get('SLACK_TOKEN', None)

if TOKEN == None:
    print("""
##################################################
# ERROR
#
# Configure your Slack Token first for test
##################################################
example)

export SLACK_TOKEN=<YOUR_SLACK_TOKEN>

""")
    exit


class TestSlackNotification(TestCase):
    config = utils.load_yaml_from_file(
        os.environ.get('SPACEONE_TEST_CONFIG_FILE', './config.yml'))
    endpoints = config.get('ENDPOINTS', {})
    secret_data = {}
    channel_data = {
        'token': TOKEN,
        'channel': 'everyone'
    }

    def test_init(self):
        v_info = self.notification.Protocol.init({'options': {}})
        print_json(v_info)

    def test_verify(self):
        options = {}
        self.notification.Protocol.verify({'options': options, 'secret_data': self.secret_data})

    def test_dispatch(self):
        options = {}

        self.notification.Notification.dispatch({
            'options': options,
            'message': {
                'title': 'This is sample notification',
                'description': 'SAL LYO JU SE YO.\nDom Whang Cha\n',
                'tags': {
                    'project_id': 'project-xxxxx',
                    'project_name': '스페이스원 웹서버',
                    'resource_id': 'server-yyyyy',
                    'resource_name': 'web-server-001'
                },
                'callbacks': [{
                    'label': 'Acknowledge SpaceONE Alerts',
                    'url': 'https://google.com'
                }]
            },
            'notification_type': 'INFO',
            'secret_data': self.secret_data,
            'channel_data': self.channel_data
        })

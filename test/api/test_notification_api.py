import os
import logging
import time

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
                'title_link': 'https://spaceone.console.doodle.spaceone.dev/monitoring/alert-manager/escalation-policy',
                'description': 'SAL LYO JU SE YO.\n돔 - 황 - ㅊ ㅑ \n',
                'tags': [
                    {
                        'key': 'project_id',
                        'value': 'project-xxxxx',
                        'options': {'short': True}
                    },
                    {
                        'key': 'project_name',
                        'value': '스페이스원 웹서버',
                        'options': {'short': True}
                    },
                    {
                        'key': 'resource_id',
                        'value': 'Resource [Asia Pacific (Seoul)]:[AWS/NetworkELB]: net/af83f347171a044af96459ebb37c8225/743a23562a96c595'
                    },

                ],
                'callbacks': [{
                    'label': 'Acknowledge SpaceONE Alerts',
                    'url': 'https://monitoring-webhook.dev.spaceone.dev/monitoring/v1/alert/alert-61afa17a25bf/4186dacf2d69a689ca4dbed965ef6e2d/ACKNOWLEDGED'
                }],
                'timestamp': str(time.time())
            },
            'notification_type': 'WARNING',
            'secret_data': self.secret_data,
            'channel_data': self.channel_data
        })

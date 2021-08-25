import time
import logging

from spaceone.core import utils
from spaceone.core.service import *
from spaceone.notification.conf.slack_conf import SLACK_CONF
from spaceone.notification.manager.notification_manager import NotificationManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
class NotificationService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)

    @transaction
    @check_required(['options', 'message', 'notification_type'])
    def dispatch(self, params):
        """
        Args:
            params:
                - options
                - message
                - notification_type
                - secret_data
                - channel_data
        """
        channel_data = params.get('channel_data', {})
        notification_type = params['notification_type']
        message = params['message']
        kwargs = {}

        slack_token = channel_data.get('token')
        channel = channel_data.get('channel')

        noti_mgr: NotificationManager = self.locator.get_manager('NotificationManager')
        message_block = []
        message_attachment = self.make_slack_message_attachment(message, notification_type)

        if message_attachment:
            kwargs = {
                'attachments': message_attachment
            }

        noti_mgr.dispatch(slack_token, channel, message_block, **kwargs)

    def make_slack_message_attachment(self, message, notification_type):
        '''
        message (dict): {
            'title': 'str',
            'link': 'str',
            'description': bool,
            'tags': [
                {
                    'key': '',
                    'value': '',
                    'options': {
                        'short': true|false
                    }
                }
            ],
            'callbacks': [
              {
                'label': 'str',
                'url': 'str',
                'options': 'dict'
              }
            ],
            'occurred_at': 'iso8601'
        }
        '''
        attachments = []

        attachment = {
            "pretext": message.get('title', ''),
            "color": self.get_message_attachment_color(notification_type),
            "text": f"{message.get('description', '')}",
            'mrkdwn_in': ['text'],
            'footer': SLACK_CONF['footer'],
            'footer_icon': SLACK_CONF['footer_icon_url']
        }

        if 'link' in message:
            attachment.update({
                'title': message.get('title', ''),
                'title_link': message.get('link'),
            })

        if 'tags' in message:
            attachment['fields'] = self.make_fields_from_tags(message['tags'])

        if 'callbacks' in message:
            attachment['actions'] = self.make_callback_buttons_in_attachment(message['callbacks'])

        if 'occured_at' in message:
            if timestamp := self.convert_occured_at_format(message['occured_at']):
                attachment.update({'ts': timestamp})

        attachments.append(attachment)
        return attachments

    @staticmethod
    def make_callback_buttons_in_attachment(callbacks):
        actions = []

        for _callback in callbacks:
            actions.append({
                'name': _callback.get('label', ''),
                'text': _callback.get('label', ''),
                'type': 'button',
                'style': 'danger',
                "url": f"{_callback.get('url', '')}",
            })

        return actions

    @staticmethod
    def get_message_attachment_color(notification_type):
        color_map = SLACK_CONF.get('attachment_color_map', {})
        return color_map.get(notification_type, color_map.get('default', '#858895'))

    @staticmethod
    def make_fields_from_tags(tags):
        fields = []

        for tag_info in tags:
            field = {
                'title': tag_info.get("key", ""),
                'value': tag_info.get("value", ""),
            }

            if options := tag_info.get('options'):
                if 'short' in options:
                    field.update({'short': options['short']})

            fields.append(field)

        return fields

    @staticmethod
    def convert_occured_at_format(occured_at):
        if dt := utils.iso8601_to_datetime(occured_at):
            return time.mktime(dt.timetuple())
        return None

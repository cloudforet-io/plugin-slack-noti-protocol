import logging

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
        # message_block = self.make_slack_message_block(message, notification_type)
        message_block = []
        message_attachment = self.make_slack_message_attachment(message, notification_type)

        if message_attachment:
            kwargs = {
                'attachments': message_attachment
            }

        noti_mgr.dispatch(slack_token, channel, message_block, **kwargs)

    def make_slack_message_block(self, message, notification_type):
        '''
        message (dict): {
            'title': 'str',
            'description': bool,
            'tags': dict,
            'callbacks': [
              {
                'label': 'str',
                'url': 'str',
                'options': 'dict'
              }
            ]
        }
        '''

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"[{notification_type}] {message.get('title', '')}"
                }
            }
        ]

        contexts = self.make_contexts_from_tags(message.get('tags', {}))
        if contexts:
            blocks.extend(contexts)

        buttons = self.make_callback_buttons(message.get('callbacks', []))
        if buttons:
            blocks.append({
                "type": "actions",
                "elements": buttons
            })

        return blocks

    def make_slack_message_attachment(self, message, notification_type):
        '''
        message (dict): {
            'title': 'str',
            'description': bool,
            'tags': dict,
            'callbacks': [
              {
                'label': 'str',
                'url': 'str',
                'options': 'dict'
              }
            ]
        }
        '''
        attachments = []

        attachment = {
            "pretext": f"[{notification_type}] {message.get('title', '')}",
            "color": self.get_message_attachment_color(notification_type),
            "text": f"{message.get('description', '')}",
            'mrkdwn_in': ['text'],
            'footer': 'From. SpaceONE',
            'footer_icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/wanny.png'
        }

        if 'tags' in message:
            attachment['fields'] = self.make_fields_from_tags(message['tags'])

        if 'callbacks' in message:
            attachment['actions'] = self.make_callback_buttons_in_attachment(message['callbacks'])

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
    def make_callback_buttons(callbacks):
        buttons = []

        for callback in callbacks:
            button_element = {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": f"{callback.get('label', 'OK')}"
                },
                "url": f"{callback.get('url', '')}",
                "style": "danger"
            }

            if 'options' in callback:
                button_element.update(callback['options'])

            buttons.append(button_element)

        return buttons

    @staticmethod
    def make_contexts_from_tags(tags):
        contexts = []

        for key, value in tags.items():
            contexts.append({
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": f"- {key}: {value}",
                    }
                ]
            })

        return contexts

    @staticmethod
    def make_fields_from_tags(tags):
        fields = []

        for key, value in tags.items():
            fields.append({
                'title': f'{key}',
                'value': f'{value}',
                'short': True
            })

        return fields
import logging

from spaceone.core.service import *
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
        secret_data = params.get('secret_data', {})
        channel_data = params.get('channel_data', {})
        notification_type = params['notification_type']
        message = params['message']
        kwargs = {}

        slack_token = secret_data.get('token')
        channel = channel_data.get('channel')

        noti_mgr: NotificationManager = self.locator.get_manager('NotificationManager')
        message_block = self.make_slack_message_block(message)
        noti_mgr.dispatch(slack_token, channel, message_block, **kwargs)

    def make_slack_message_block(self, message):
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
                    "text": f"{message.get('title', '')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"{message.get('description', '')}"
                }
            }
        ]

        contexts = self.make_contexts_from_tags(message.get('tags', {}))
        if contexts:
            blocks.extend(contexts)

        buttons = self.make_callback_button(message.get('callbacks', []))
        if buttons:
            blocks.append({
                "type": "actions",
                "elements": buttons
            })

        return blocks

    @staticmethod
    def make_callback_button(callbacks):
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

import logging
from ssl import SSLContext
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from spaceone.core.connector import BaseConnector

__all__ = ['SlackConnector']
_LOGGER = logging.getLogger(__name__)

sslcert = SSLContext()

class SlackConnector(BaseConnector):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = WebClient(token=kwargs.get('token'), ssl=sslcert)

    def chat_message(self, channel, blocks, **kwargs):
        response = self.client.chat_postMessage(channel=f'#{channel}', blocks=blocks, **kwargs)
        return response

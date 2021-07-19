import logging
from spaceone.core.service import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
class ProtocolService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)

    @check_required(['options'])
    def init(self, params):
        """ init plugin by options
        """
        return {'metadata': {
            'data_type': 'SECRET',
            'data': {
                'schema': {
                    'properties': {
                        'token': {
                            'description': 'App-Level token value to control your Slack app',
                            'minLength': 4,
                            'title': 'Slack Token',
                            'type': 'string',
                            'examples': ['xoxb-123456789012-0987654321098-ABCDEFG']
                        },
                        'channel': {
                            'description': 'Slack channel to be received messages in your workspace',
                            'minLength': 4,
                            'title': 'Slack Channel',
                            'type': 'string',
                            'examples': ['everyone']
                        }
                    },
                    'required': [
                        'token',
                        'channel'
                    ],
                    'type': 'object'
                }
            }
        }}

    @transaction
    @check_required(['options'])
    def verify(self, params):
        """
        Args:
              params:
                - options
                - secret_data
        """
        options = params['options']
        secret_data = params.get('secret_data', {})

        return {}

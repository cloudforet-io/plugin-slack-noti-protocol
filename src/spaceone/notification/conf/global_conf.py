CONNECTORS = {
}

LOG = {
    'filters': {
        'masking': {
            'rules': {
                'Protocol.verify': [
                    'secret_data'
                ],
                'Notification.dispatch': [
                    'secret_data'
                ]
            }
        }
    }
}

HANDLERS = {
}

ENDPOINTS = {
}

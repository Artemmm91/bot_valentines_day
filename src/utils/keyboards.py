import json

from config.message_config import ASK_INFO, ASK_DECLARATION, DECLARATION_CONFIRM
from config.system_config import WATCH_USER_WITH_WAIT_DECLARATION_COMMAND, ANALYZE_COMMAND

INFO_AND_DECLARE_KEYBOARD = json.dumps(
    {
        "one_time": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": ASK_INFO.capitalize(),
                    },
                    "color": "primary"
                },
                {
                    "action": {
                        "type": "text",
                        "label": ASK_DECLARATION.capitalize(),
                    },
                    "color": "positive"
                }
            ]
        ],
    }
)

EMPTY_KEYBOARD = json.dumps(
    {
        "one_time": True,
        "buttons": [],
    }
)

CONFIRM_KEYBOARD = json.dumps(
    {
        "one_time": True,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Отмена",
                    },
                    "color": "negative"
                },
                {
                    "action": {
                        "type": "text",
                        "label": DECLARATION_CONFIRM.capitalize(),
                    },
                    "color": "positive"
                }
            ]
        ],
    }
)

ADMIN_KEYBOARD = json.dumps(
    {
        "one_time": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": WATCH_USER_WITH_WAIT_DECLARATION_COMMAND[0].capitalize(),
                    },
                    "color": "primary"
                },
                {
                    "action": {
                        "type": "text",
                        "label": ANALYZE_COMMAND[0].capitalize(),
                    },
                    "color": "negative"
                }
            ]
        ],
    }
)

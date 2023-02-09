from datetime import datetime

from config.system_config import CURRENT_TIMEZONE


def get_current_time():
    return datetime.now(CURRENT_TIMEZONE)


def get_time_id():
    return int(10 * get_current_time().timestamp())

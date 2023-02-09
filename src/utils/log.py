import sys

from utils.current_time import get_current_time


def log(log_string):
    print(f"{get_current_time().strftime('%y.%m.%d %H:%M:%S')}: {log_string}", file=sys.stderr)

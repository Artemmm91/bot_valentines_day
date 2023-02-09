from datetime import datetime

import pytz

CURRENT_TIMEZONE = pytz.timezone('Europe/Moscow')
MAX_MESSAGE_LENGTH = 4000
MAX_ATTEMPT_NUMBER = 100
LINK_TO_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSc_IrxodSrl-uhwD2JSaaeyhO6nb0H28CveKtvykpRiwXwJgw/viewform"
FORM_FIELD_NAME_TO_ID = {
    "name": 26555932,
    "vk_page_link": 1547003772,
    "sex": 1238631378,
    "sex_of_partner": 2015134065,
}
ADMIN_ID = 496062077
ADMIN_CHAT = 2000000001
START_VALENTINES_DAY = CURRENT_TIMEZONE.localize(datetime.strptime("2021.02.14 15 00", "%Y.%m.%d %H %M"))
STOP_VALENTINES_DAY = CURRENT_TIMEZONE.localize(datetime.strptime("2021.02.15 00 00", "%Y.%m.%d %H %M"))
WATCH_USER_WITH_WAIT_DECLARATION_COMMAND = ['ожидающие', 'лс', 'ls', 'ож']
ANALYZE_COMMAND = ['анализировать', 'analyze']
SEND_MATCHES_COMMAND = "send_matches"
USER_TO_MATCH = 10
USER_TO_MATCH_WITH_STOCK = 15
MAX_QUERY_IN_EXECUTE = 25

from vk_api.execute import VkFunction

from config.secret_config import FORM_ANSWER_SPREADSHEET_ID
from config.system_config import MAX_QUERY_IN_EXECUTE, ADMIN_CHAT
from table_api.connect_to_google_api import connect_to_google_api
from table_api.user_with_matches import UserWithMatches
from utils.parse_message import parse_name_from_link
from utils.secure_vk_api import SecureVkApi
from vk_api.exceptions import ApiError


def send_match_message(sheet_name):
    sheet = connect_to_google_api().spreadsheets()
    result = sheet.values().get(spreadsheetId=FORM_ANSWER_SPREADSHEET_ID,
                                range=sheet_name,
                                valueRenderOption='FORMATTED_VALUE',
                                dateTimeRenderOption='FORMATTED_STRING').execute()
    data = result['values']
    current_row = 0
    last_query = 0
    users = []
    vk = SecureVkApi()
    while current_row < len(data):
        name = data[current_row][0]
        vk_link = data[current_row][2]
        matches = []
        current_row += 1
        while data[current_row][0] == '':
            if len(data[current_row]) < 6 or data[current_row][5] != '-':
                matches.append(data[current_row])
            current_row += 1

        current_row += 1
        users.append(UserWithMatches(name, vk_link, matches))
        if len(users) - last_query == MAX_QUERY_IN_EXECUTE:
            set_id_from_screen_name(last_query, users, vk)
            last_query = len(users)

    if len(users) - last_query > 0:
        set_id_from_screen_name(last_query, users, vk)

    for user in users:
        if user.vk_id is not None:
            try:
                vk.send_message(user.get_message(), user_id=user.vk_id)
            except ApiError:
                vk.send_message(f"Not sent to {user.vk_link} (Exception)\n{user.get_message()}", peer_id=ADMIN_CHAT)
        else:
            vk.send_message(f"Not sent to {user.vk_link} (No such screen name)\n{user.get_message()}",
                            peer_id=ADMIN_CHAT)
    vk.send_message("Send matches done", peer_id=ADMIN_CHAT)


def set_id_from_screen_name(last_query, users, vk):
    query = "return ["
    count_to_execute = 0
    for user_id in range(last_query, len(users)):
        user_screen_name = parse_name_from_link(users[user_id].vk_link)
        if user_screen_name is not None:
            count_to_execute += 1
            users[user_id].vk_id = "WAIT"
            query += "API.utils.resolveScreenName({\"screen_name\": \"" + user_screen_name + "\"}),"
    if count_to_execute:
        query += "];"
        response = vk.ask_api(lambda vk_lambda: VkFunction(code=query)(vk_lambda))
        current_user = last_query
        for data in response:
            if users[current_user].vk_id != "WAIT":
                current_user += 1
            if data and data['type'] == 'user':
                users[current_user].vk_id = data['object_id']
            else:
                users[current_user].vk_id = None

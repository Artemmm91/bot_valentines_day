from config.secret_config import FORM_ANSWER_SPREADSHEET_ID
from config.system_config import ADMIN_CHAT, USER_TO_MATCH_WITH_STOCK, USER_TO_MATCH
from config.table_config import FIST_QUERY_COLUMN, DETAILED_QUESTION_COLUMN, HOLE_ANALYZE_TABLE_DATA_RANGE, NAME_COLUMN, \
    VK_LINK_COLUMN, MY_GENDER_COLUMN, MY_PARTNER_GENDER_COLUMN
from table_api.connect_to_google_api import connect_to_google_api
from table_api.user_to_analyze import UserToAnalyze
from utils import gender
from utils.secure_vk_api import SecureVkApi
from utils.current_time import get_time_id


def analyze():
    sheet = connect_to_google_api().spreadsheets()
    result = sheet.values().get(spreadsheetId=FORM_ANSWER_SPREADSHEET_ID,
                                range=HOLE_ANALYZE_TABLE_DATA_RANGE,
                                valueRenderOption='FORMATTED_VALUE',
                                dateTimeRenderOption='FORMATTED_STRING').execute()
    data = result['values']
    possible_answers = get_possible_answers(data)
    users = prepare_data(data, possible_answers)

    result_sheet_data = []
    for i in range(len(users)):
        user_match_to_i = []
        for j in range(len(users)):
            if i == j or not gender.is_can_be_a_partner(users[i], users[j]):
                continue
            user_match_to_i.append((users[i].count_match(users[j]), users[j]))
        user_match_to_i.sort(key=lambda x: x[0], reverse=True)
        add_to_result_sheet_data(result_sheet_data, users[i], user_match_to_i)

    if result_sheet_data:
        result_sheet, result_sheet_id = add_sheet(sheet, len(result_sheet_data), 7)
        sheet.values().update(spreadsheetId=FORM_ANSWER_SPREADSHEET_ID, valueInputOption="RAW", range=result_sheet,
                              body={
                                  "majorDimension": "ROWS",
                                  "values": result_sheet_data
                              }).execute()
        set_dimension_property(sheet, result_sheet_id, {0: 150, 1: 150, 2: 150, 3: 1000, 4: 30, 5: 30})

        SecureVkApi().send_message(result_sheet, peer_id=ADMIN_CHAT)
        SecureVkApi().send_message(f"https://docs.google.com/spreadsheets/d/{FORM_ANSWER_SPREADSHEET_ID}/edit#gid={result_sheet_id}",
                                   peer_id=ADMIN_CHAT)
    else:
        SecureVkApi().send_message("Nothing to send", peer_id=ADMIN_CHAT)


def get_possible_answers(data):
    possible_answers = [set() for _ in range(FIST_QUERY_COLUMN, DETAILED_QUESTION_COLUMN)]
    for user_answer in data:
        for query_id in range(FIST_QUERY_COLUMN, DETAILED_QUESTION_COLUMN):
            possible_answers[query_id - FIST_QUERY_COLUMN].add(user_answer[query_id])
    return [list(possible_answer) for possible_answer in possible_answers]


def prepare_data(data, possible_answers):
    pretty_data = []
    for user_answer in data:
        index_answer = []
        for query_id in range(FIST_QUERY_COLUMN, DETAILED_QUESTION_COLUMN):
            for i in range(len(possible_answers[query_id - FIST_QUERY_COLUMN])):
                if user_answer[query_id] == possible_answers[query_id - FIST_QUERY_COLUMN][i]:
                    index_answer.append(i)
                    break
        pretty_data.append(UserToAnalyze(user_answer[NAME_COLUMN], user_answer[VK_LINK_COLUMN],
                                         gender.get(user_answer[MY_GENDER_COLUMN]),
                                         gender.get(user_answer[MY_PARTNER_GENDER_COLUMN]),
                                         index_answer,
                                         user_answer[DETAILED_QUESTION_COLUMN],
                                         len(pretty_data)))
    return pretty_data


def add_sheet(sheet, row_count, column_count):
    sheet_title = f"Analyze-{get_time_id()}"
    result = sheet.batchUpdate(spreadsheetId=FORM_ANSWER_SPREADSHEET_ID, body={
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": sheet_title,
                        "gridProperties":
                            {
                                "rowCount": row_count,
                                "columnCount": column_count,
                            }
                    }
                }
            }
        ]
    }).execute()
    return sheet_title, result['replies'][0]['addSheet']['properties']['sheetId']


def add_to_result_sheet_data(result_sheet_data, user, user_match):
    result_sheet_data.append([user.name, '', user.vk_link, user.detailed_answer])
    index = 0
    for match_count, partner in user_match:
        index += 1
        row = ['', partner.name, partner.vk_link, partner.detailed_answer, match_count]
        if index > USER_TO_MATCH:
            row.append('-')
        result_sheet_data.append(row)
        if index >= USER_TO_MATCH_WITH_STOCK:
            break
    result_sheet_data.append(['-' * 50, '-' * 50, '-' * 50, '-' * 300, '-' * 50, '-' * 50])


def set_dimension_property(sheet, sheet_id, dimension_info):
    requests = []
    for column, size in dimension_info.items():
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": column,
                    "endIndex": column + 1,
                },
                "properties": {
                    "pixelSize": size
                },
                "fields": "pixelSize"
            }
        })
    sheet.batchUpdate(spreadsheetId=FORM_ANSWER_SPREADSHEET_ID, body={"requests": requests}).execute()

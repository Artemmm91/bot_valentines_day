from config.system_config import ADMIN_ID
from config.table_config import DECLARATION_COUNTER_TABLE_NAME, DECLARATION_TABLE_NAME
from table_api.connect_to_google_api import connect_to_google_api
from utils.parse_message import parse_name_from_link


def get_new_declarations(spreadsheet_id, vk_api):
    service = connect_to_google_api().spreadsheets()
    spreadsheet = service.get(spreadsheetId=spreadsheet_id).execute()
    sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets')]
    if DECLARATION_COUNTER_TABLE_NAME not in sheets:
        add_counter_sheet(service, spreadsheet_id)
    metadata = service.values().get(spreadsheetId=spreadsheet_id,
                                    range=f"'{DECLARATION_COUNTER_TABLE_NAME}'!B1:B4",
                                    valueRenderOption='FORMATTED_VALUE',
                                    dateTimeRenderOption='FORMATTED_STRING').execute()['values']
    current_counter = int(metadata[1][0])
    declaration_to_send_number = int(metadata[0][0])
    announce_at_all = int(metadata[2][0])
    announce_sent = int(metadata[3][0])
    send_announce(announce_sent, announce_at_all, vk_api, service, spreadsheet_id)
    if current_counter < declaration_to_send_number:
        data = service.values().get(spreadsheetId=spreadsheet_id,
                                    range=f"'{DECLARATION_TABLE_NAME}'!B{current_counter + 2}"
                                          f":C{declaration_to_send_number + 1}",
                                    valueRenderOption='FORMATTED_VALUE',
                                    dateTimeRenderOption='FORMATTED_STRING').execute()['values']
        declaration = []
        for row in data:
            name = parse_name_from_link(row[0])
            if name is None:
                name = f"id{ADMIN_ID}"
                row[1] = f"{row[0]} not parsed"
            declaration.append({"name": name, "text": row[1]})

        service.values().update(spreadsheetId=spreadsheet_id, valueInputOption="RAW",
                                range=f"'{DECLARATION_COUNTER_TABLE_NAME}'!B2",
                                body={
                                    "majorDimension": "ROWS",
                                    "values": [[declaration_to_send_number]]
                                }).execute()

        return declaration
    else:
        return []


def send_announce(announce_sent, announce_at_all, vk_api, service, spreadsheet_id):
    if announce_sent < announce_at_all:
        vk_api.send_message(f"{announce_at_all - announce_sent} new declarations", user_id=ADMIN_ID)
        service.values().update(spreadsheetId=spreadsheet_id, valueInputOption="RAW",
                                range=f"'{DECLARATION_COUNTER_TABLE_NAME}'!B4",
                                body={
                                    "majorDimension": "ROWS",
                                    "values": [[announce_at_all]]
                                }).execute()


def add_counter_sheet(service, spreadsheet_id):
    service.batchUpdate(spreadsheetId=spreadsheet_id, body={
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": DECLARATION_COUNTER_TABLE_NAME,
                        "gridProperties":
                            {
                                "rowCount": 4,
                                "columnCount": 2,
                            }
                    }
                }
            }
        ]
    }).execute()
    service.values().update(spreadsheetId=spreadsheet_id, valueInputOption="USER_ENTERED",
                            range=DECLARATION_COUNTER_TABLE_NAME,
                            body={
                                "majorDimension": "ROWS",
                                "values": [["Признаний в таблице готовых к отправке:", 0],
                                           ["Признаний обработано:", 0],
                                           ["Признаний в таблице:", f"=СЧЁТЗ('Ответы на форму'!A:A)-1"],
                                           ["Оповещений отправлено:", 0]]
                            }).execute()

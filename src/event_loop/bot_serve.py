import json
import re
import time
import traceback
from multiprocessing import Process

from vk_api.bot_longpoll import VkBotEventType
from vk_api.vk_api import VkApiGroup
from vk_api.exceptions import ApiError

from event_loop.secure_vk_bot_long_poll import SecureVkBotLongPoll
from config.message_config import START_MESSAGE_AFTER, ASK_START, INFO_MESSAGE_AFTER, ASK_INFO, ASK_DECLARATION, \
    DECLARATION_ASK_FOR_NAME, DECLARATION_INCORRECT_NAME, DECLARATION_ASK_FOR_CONFIRM, \
    DECLARATION_CONFIRM, DECLARATION_ASK_FOR_TEXT, DECLARATION_CONFIRM_CANCEL, DECLARATION_CONFIRM_SEND, \
    DECLARATION_SEND_PROBLEM, DECLARATION_SEND_NOT_A_USER, MESSAGE_WITH_DECLARATION, START_MESSAGE_IN, \
    INFO_MESSAGE_IN, MESSAGE_ABOUT_WAIT_DECLARATION
from config.secret_config import VK_TOKEN, GROUP_ID, DECLARATION_SPREADSHEET_ID
from config.system_config import ADMIN_ID, ADMIN_CHAT, START_VALENTINES_DAY, STOP_VALENTINES_DAY, \
    WATCH_USER_WITH_WAIT_DECLARATION_COMMAND, ANALYZE_COMMAND, SEND_MATCHES_COMMAND
from table_api.form_analyze import analyze
from table_api.get_new_declarations import get_new_declarations
from table_api.send_match_message import send_match_message
from utils import status
from utils.secure_vk_api import SecureVkApi
from utils.create_link import create_form_link
from utils.current_time import get_current_time
from utils.keyboards import INFO_AND_DECLARE_KEYBOARD, EMPTY_KEYBOARD, CONFIRM_KEYBOARD, ADMIN_KEYBOARD
from utils.log import log
from utils.data_base import DataBase
from utils.parse_message import parse_name_message
from utils.send_declaration_status import SEND_NORMAL, SEND_PROBLEM, NOT_A_USER


class BotServe:
    def __init__(self):
        self.__vk_api = SecureVkApi()
        self.__data_base = DataBase()
        self.__last_event = None
        self.work = True

    def get_last_event(self):
        return self.__last_event

    def serve(self, last_event):
        if last_event is not None:
            log(f"Handle event from previous time {last_event}")
            self.__handle_event(last_event)

        log("--------------- Serve started")
        for event in SecureVkBotLongPoll(VkApiGroup(token=VK_TOKEN), group_id=GROUP_ID).listen():
            log(event)
            self.__last_event = event
            self.__handle_event(event)
            self.__last_event = None

    def __handle_event(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW and event.message.text != '':
            if event.from_user:
                self.__handle_message_from_user(event)
            elif event.from_chat:
                self.__handle_message_in_chat(event)

    def __handle_message_from_user(self, event):
        if get_current_time() < STOP_VALENTINES_DAY:
            user, session = self.__data_base.get_user_by_id(event.message.from_id)
            log(f"User: {user}")
            if user.status != "":
                if user.status[:3] == status.Declaration.get_base_name():
                    self.__handle_declaration_message(user, session, event)
            else:
                lower_message = event.message.text.lower()
                if lower_message in ASK_START:
                    self.__handle_start_message(user.id)
                elif lower_message == ASK_INFO:
                    self.__handle_info_message(user.id)
                elif lower_message == ASK_DECLARATION:
                    self.__handle_first_declaration_message(user, session)
            self.__send_exists_declarations(user.id)
            session.close()

    def __handle_message_in_chat(self, event):
        if event.message.peer_id == ADMIN_CHAT:
            message = event.message.text
            command_re = re.compile(fr"^\[club{GROUP_ID}\|[^]]+][ ]+(\S+)")
            command_message = message.split()[0].lower()
            search = command_re.search(message)
            if search:
                command_message = search.group(1).lower()
            if command_message in WATCH_USER_WITH_WAIT_DECLARATION_COMMAND:
                user_with_wait_declaration = self.__data_base.get_user_with_wait_declaration()
                if len(user_with_wait_declaration) != 0:
                    self.__vk_api.send_message("\n".join(user_with_wait_declaration), peer_id=event.message.peer_id,
                                               keyboard=ADMIN_KEYBOARD)
                else:
                    self.__vk_api.send_message("empty", peer_id=event.message.peer_id, keyboard=ADMIN_KEYBOARD)
            elif command_message in ANALYZE_COMMAND:
                Process(target=analyze).start()
            elif len(message) >= 2 and message.split()[0] == SEND_MATCHES_COMMAND:
                Process(target=send_match_message, args=(event.message.text.split()[1],)).start()

    def __handle_start_message(self, user_id):
        self.__send_message_with_form(START_MESSAGE_AFTER, START_MESSAGE_IN, user_id)

    def __send_exists_declarations(self, user_id):
        declarations = self.__data_base.get_all_wait_declaration_for_user(user_id)
        if len(declarations) > 0:
            self.__vk_api.send_message(MESSAGE_ABOUT_WAIT_DECLARATION.format(len(declarations)), user_id=user_id,
                                       keyboard=INFO_AND_DECLARE_KEYBOARD)
            for declaration in declarations:
                if declaration[1] == '':
                    self.__vk_api.send_message(declaration[0], user_id=user_id)
                else:
                    self.__vk_api.send_message(declaration[0], user_id=user_id, content_source=declaration[1])

    def __handle_info_message(self, user_id):
        self.__send_message_with_form(INFO_MESSAGE_AFTER, INFO_MESSAGE_IN, user_id)

    def __send_message_with_form(self, message_text_after, message_text_in, user_id):
        if get_current_time() < START_VALENTINES_DAY:
            user_info = self.__vk_api.ask_api(lambda vk: vk.users.get(user_ids=user_id, fields="sex,screen_name")[0])
            form_link = create_form_link(user_info)
            self.__vk_api.send_message(message_text_after.format(form_link), user_id=user_id,
                                       keyboard=INFO_AND_DECLARE_KEYBOARD)
        else:
            self.__vk_api.send_message(message_text_in, user_id=user_id, keyboard=INFO_AND_DECLARE_KEYBOARD)

    def __handle_first_declaration_message(self, user, session):
        self.__vk_api.send_message(DECLARATION_ASK_FOR_NAME, user_id=user.id, keyboard=EMPTY_KEYBOARD)
        user.status = status.Declaration.get_info_status(status.Declaration.WAIT_FOR_NAME)
        session.commit()

    def __handle_declaration_message(self, user, session, event):
        info_status = user.status[3:6]
        if info_status == status.Declaration.WAIT_FOR_NAME:
            name = parse_name_message(event.message.text)
            if name is None:
                self.__vk_api.send_message(DECLARATION_INCORRECT_NAME, user_id=user.id, keyboard=EMPTY_KEYBOARD)
            else:
                user.status = status.Declaration.get_info_status(status.Declaration.WAIT_FOR_TEXT) + json.dumps(
                    {"name": name})
                session.commit()
                self.__vk_api.send_message(DECLARATION_ASK_FOR_TEXT, user_id=user.id, keyboard=EMPTY_KEYBOARD)
        elif info_status == status.Declaration.WAIT_FOR_TEXT:
            data = json.loads(user.status[6:])
            data['text'] = event.message.text
            data['get_text_from'] = event.message.id
            user.status = status.Declaration.get_info_status(status.Declaration.WAIT_FOR_CONFIRM) + json.dumps(data)
            session.commit()
            self.__vk_api.send_message(DECLARATION_ASK_FOR_CONFIRM.format(data['name'], data['text']), user_id=user.id,
                                       keyboard=CONFIRM_KEYBOARD,
                                       content_source=json.dumps({"type": "message", "owner_id": GROUP_ID,
                                                                  "peer_id": event.message.peer_id,
                                                                  "conversation_message_id": data[
                                                                      'get_text_from']}))
        elif info_status == status.Declaration.WAIT_FOR_CONFIRM:
            if event.message.text.lower() == DECLARATION_CONFIRM:
                data = json.loads(user.status[6:])
                send_result = self.__send_declaration_to_other_user(data, event)
                if send_result == SEND_NORMAL:
                    message_to_send = DECLARATION_CONFIRM_SEND
                elif send_result == SEND_PROBLEM:
                    message_to_send = DECLARATION_SEND_PROBLEM
                else:
                    message_to_send = DECLARATION_SEND_NOT_A_USER.format(data['name'])
                self.__vk_api.send_message(message_to_send, user_id=user.id, keyboard=INFO_AND_DECLARE_KEYBOARD)
            else:
                self.__vk_api.send_message(DECLARATION_CONFIRM_CANCEL, user_id=user.id,
                                           keyboard=INFO_AND_DECLARE_KEYBOARD)
            user.status = ""
            session.commit()
        else:
            self.__vk_api.send_message(f"Status error @{user.id}\nStatus: \"{user.status}\"", user_id=ADMIN_ID)
            user.status = ""
            session.commit()

    def __send_declaration_to_other_user(self, data, event=None):
        user_send_to = self.__vk_api.ask_api(lambda vk: vk.utils.resolveScreenName(screen_name=data['name']))
        if user_send_to == [] or user_send_to['type'] != "user" or user_send_to.get('object_id') is None:
            return NOT_A_USER
        user_send_to_id = user_send_to['object_id']
        try:
            if event is None:
                self.__vk_api.send_message(MESSAGE_WITH_DECLARATION.format(data['text']), user_id=user_send_to_id)
            else:
                self.__vk_api.send_message(MESSAGE_WITH_DECLARATION.format(data['text']), user_id=user_send_to_id,
                                           content_source=json.dumps({"type": "message", "owner_id": GROUP_ID,
                                                                      "peer_id": event.message.peer_id,
                                                                      "conversation_message_id": data[
                                                                          'get_text_from']}))
            return SEND_NORMAL
        except ApiError as e:
            log(f"Message not sent due to {e}")
            if event is None:
                self.__data_base.add_wait_declaration(user_send_to_id, data['text'], '')
            else:
                self.__data_base.add_wait_declaration(user_send_to_id, data['text'],
                                                      json.dumps({"type": "message", "owner_id": GROUP_ID,
                                                                  "peer_id": event.message.peer_id,
                                                                  "conversation_message_id": data[
                                                                      'get_text_from']}))
            self.__vk_api.send_message(f"Сообщение @id{user_send_to_id}", peer_id=ADMIN_CHAT)
            self.__vk_api.send_message(data['text'], peer_id=ADMIN_CHAT)
            return SEND_PROBLEM

    def send_declaration_from_table(self):
        while self.work:
            try:
                self.__send_new_declaration_from_table()
            except Exception as e:
                log(e)
                traceback.print_exc()
                SecureVkApi().send_message(f"Exception(send_declaration_from_table): {e}", user_id=ADMIN_ID)
            finally:
                time.sleep(60)

    def __send_new_declaration_from_table(self):
        new_declarations = get_new_declarations(DECLARATION_SPREADSHEET_ID, self.__vk_api)
        for declaration in new_declarations:
            result = self.__send_declaration_to_other_user(declaration)
            if result == NOT_A_USER:
                self.__vk_api.send_message(
                    f"В таблице указан не пользователь {declaration['name']} (@{declaration['name']})",
                    peer_id=ADMIN_CHAT)

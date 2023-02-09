import time

import requests
from vk_api.vk_api import VkApiGroup
from vk_api.exceptions import ApiError

from config.secret_config import VK_TOKEN
from config.system_config import MAX_MESSAGE_LENGTH
from utils.current_time import get_time_id
from utils.log import log


class SecureVkApi:
    def __init__(self):
        self.__set_vk_api()

    def send_message(self, message, **kwargs):
        send = 0

        while send < len(message):
            self.ask_api(lambda vk: vk.messages.send(message=message[send:send + MAX_MESSAGE_LENGTH],
                                                     random_id=get_time_id(), **kwargs))
            send += MAX_MESSAGE_LENGTH

    def ask_api(self, func):
        try:
            return func(self.__vk)
        except requests.exceptions.ConnectionError:
            log("---------------- Reconnect to vk")
            self.__set_vk_api()
            return func(self.__vk)
        except ApiError as e:
            log(f"---------------- {e} start")
            time.sleep(30)
            log(f"---------------- {e} end")
            self.__set_vk_api()
            return func(self.__vk)

    def __set_vk_api(self):
        self.__vk = VkApiGroup(token=VK_TOKEN).get_api()

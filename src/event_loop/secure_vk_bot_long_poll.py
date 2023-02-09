import requests
from vk_api.bot_longpoll import VkBotLongPoll

from utils.log import log


class SecureVkBotLongPoll(VkBotLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except requests.exceptions.ConnectionError:
                log("----------------- VkBotLongPoll ConnectionError Exception")
            except requests.exceptions.ReadTimeout:
                log("----------------- VkBotLongPoll ReadTimeout Exception")

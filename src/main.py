import traceback
from multiprocessing.context import Process

from event_loop.bot_serve import BotServe
from utils.secure_vk_api import SecureVkApi
from utils.log import log
from config.system_config import ADMIN_ID


def serve():
    last_event = None
    while True:
        bot = BotServe()
        Process(target=bot.send_declaration_from_table).start()
        try:
            bot.serve(last_event)
        except Exception as e:
            log(e)
            traceback.print_exc()
            last_event = bot.get_last_event()
            if last_event is not None:
                log(f"save event from last time: {last_event}")
            SecureVkApi().send_message(f"Exception: {e}", user_id=ADMIN_ID)
            log("----------------- Restart bot")
        bot.work = False


if __name__ == '__main__':
    serve()

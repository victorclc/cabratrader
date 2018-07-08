from telegram.ext import Updater
import common.helper as helper


class PushNotification(object):
    config = helper.load_config('external.cfg')['telegram']
    token = config['token']
    push_users = config['push_users']
    active = config['active']
    updater = Updater(token=token)

    @classmethod
    def send(cls, message):
        if cls.active:
            for user in cls.push_users:
                cls.updater.bot.send_message(chat_id=user, text=message)

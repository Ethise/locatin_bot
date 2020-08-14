from general_functions import message_btn, create_and_del_usr


def command_start(message, bd, bot, json_v):
    text = "Чтобы просмотреть доступные команды введите /help"
    message_btn(message, text, ("/help",), bot)
    if message.from_user.id not in bd:
        create_and_del_usr(message, bd, json_v)

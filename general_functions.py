from button import KeyboardBtn
import json


commands = ('/add', '/list', '/reset', '/start', '/help')


def get_state_usr(message, action):
    return action[message.chat.id]


def update_state_usr(message, state, action):
    action[message.chat.id] = state


def clean_json(json):
    for name_field in json:
        json[name_field] = ""


def create_and_del_usr(message, bd, json_v):
    bd.set(message.from_user.id, json.dumps(json_v))


def message_btn(message, text, btn, bot):
    buttons = KeyboardBtn(btn)
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=buttons.create_keyboard())


def back_to_help(message, bot, text="", btn=("/help",)):
    text_back = "Для отображения доступных команд введите\n/help"
    message_btn(message, text + text_back, btn, bot)


def update_bd(dict, bd, message):
    if message.from_user.id in bd:
        json_from_bd = json.loads(bd.get(message.from_user.id).decode('utf8'))
        for name_field in json_from_bd:
            json_from_bd[name_field].append(dict[name_field])
        bd.set(message.from_user.id, json.dumps(json_from_bd))
    else:
        bd.set(message.from_user.id, json.dumps(dict))

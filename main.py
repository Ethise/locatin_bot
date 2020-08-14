import telebot
from collections import defaultdict
import redis
import os
from start import command_start
from help import command_help
import add
import general_functions
import list
import reset


START_CREATE, GET_LOCATION, GET_NAME, GET_PHOTO, CONFIRM_ADD = range(5)
START_DEL, CONFIRM_DEL = range(2)
START_LIST = 0
NO_PHOTO = "Без фотографии"
USER_STATE_ADD = defaultdict(lambda: START_CREATE)
USER_STATE_DEL = defaultdict(lambda: START_DEL)
USER_STATE_LIST = defaultdict(lambda: START_LIST)
with open("token.txt", "r") as f:
    token = f.read()
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

bot = telebot.TeleBot(token)
bd = redis.from_url(redis_url)
commands = ('/add', '/list', '/reset', '/start', '/help')
yes_no_btns = ("Да", "Нет")

json_template_currently = {
    "latitude": "",
    "longitude": "",
    "name": "",
    "photo": "",
    "time": ""
}
json_template_bd = {
    "latitude": [],
    "longitude": [],
    "name": [],
    "photo": [],
    "time": []
}


def get_state_usr(message, action):
    return action[message.chat.id]


def update_state_usr(message, state, action):
    action[message.chat.id] = state


def stop_command(message, action, start_state, json_v):
    btn = ("{}".format(message.text),)
    text = 'Прерванное действие. Введите еще раз новую команду\n{}'.format(message.text)
    general_functions.message_btn(message, text, btn, bot)
    update_state_usr(message, start_state, action)
    general_functions.clean_json(json_v)


def check_not_command(message, action, start_state, json_v):
    if message.text in commands:
        stop_command(message, action, start_state, json_v)
        return False
    return True


@bot.message_handler(func=lambda x: True, commands=['start'])
def start_menu(message):
    command_start(message, bd, bot, json_template_bd)


@bot.message_handler(func=lambda x: True, commands=['help'])
def help_menu(message):
    command_help(message, bot)


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_ADD) == START_CREATE, commands=['add'])
def start_create(message):
    add.command_add_sc(message, bot)
    update_state_usr(message, GET_LOCATION, USER_STATE_ADD)


@bot.message_handler(
    func=lambda message: get_state_usr(message, USER_STATE_ADD) == GET_LOCATION,
    content_types=["location", "text"]
)
def get_location(message):
    if check_not_command(message, USER_STATE_ADD, START_CREATE, json_template_currently):
        state = GET_LOCATION
        if add.command_add_gl(message, json_template_currently, bot):
            state = GET_NAME
        update_state_usr(message, state, USER_STATE_ADD)


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_ADD) == GET_NAME, content_types=["text"])
def get_name(message):
    if check_not_command(message, USER_STATE_ADD, START_CREATE, json_template_currently):
        add.command_add_gn(message, json_template_currently, bot, NO_PHOTO)
        update_state_usr(message, GET_PHOTO, USER_STATE_ADD)


@bot.message_handler(
    func=lambda message: get_state_usr(message, USER_STATE_ADD) == GET_PHOTO,
    content_types=["photo", "text"]
)
def get_photo(message):
    if check_not_command(message, USER_STATE_ADD, START_CREATE, json_template_currently):
        add.command_add_gp(message, json_template_currently, NO_PHOTO, yes_no_btns, bot)
        update_state_usr(message, CONFIRM_ADD, USER_STATE_ADD)


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_ADD) == CONFIRM_ADD, content_types=["text"])
def confirm_add(message):
    if check_not_command(message, USER_STATE_ADD, START_CREATE, json_template_currently):
        add.command_add_ca(message, json_template_currently, bd, bot)
        update_state_usr(message, START_CREATE, USER_STATE_ADD)


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_LIST) == START_LIST, commands=['list'])
def show_list_first(message):
    next_state = list.command_list_sl(message, bd, json_template_currently, START_LIST, START_LIST, NO_PHOTO, bot)
    update_state_usr(message, next_state, USER_STATE_LIST)


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_LIST) > 0)
def show_list(message):
    if check_not_command(message, USER_STATE_LIST, START_LIST, json_template_currently):
        next_state = list.command_list_nl(
            message, get_state_usr(message, USER_STATE_LIST), START_LIST, json_template_currently, NO_PHOTO, bot
        )
        update_state_usr(message, next_state, USER_STATE_LIST)


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_DEL) == START_DEL, commands=['reset'])
def start_reset(message):
    reset.command_list_sd(message, bot, yes_no_btns)
    update_state_usr(message, CONFIRM_DEL, USER_STATE_DEL)


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_DEL) == CONFIRM_DEL)
def confirm_reset(message):
    if check_not_command(message, USER_STATE_DEL, START_DEL, json_template_currently):
        reset.command_list_cd(message, bd, json_template_bd, bot)
        update_state_usr(message, START_DEL, USER_STATE_DEL)


if __name__ == '__main__':
  bot.polling(none_stop=True)

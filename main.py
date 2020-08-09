import telebot
from collections import defaultdict
import redis
import json
import os
from button import KeyboardBtn


START_CREATE, GET_LOCATION, GET_NAME, GET_PHOTO, CONFIRM_ADD = range(5)
START_DEL, CONFIRM_DEL = range(2)
START_LIST = 0
NO_PHOTO = "Без фотографии"
BACK_TO_START = "Для отображения доступных команд введите\n/start"
USER_STATE_ADD = defaultdict(lambda: START_CREATE)
USER_STATE_DEL = defaultdict(lambda: START_DEL)
USER_STATE_LIST = defaultdict(lambda: START_LIST)
with open("token.txt", "r") as f:
    token = f.read()
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

bot = telebot.TeleBot(token)
bd = redis.from_url(redis_url)
commands = ('/add', '/list', '/reset')
yes_no_btns = KeyboardBtn(("Да", "Нет"))

json_template_currently = {
    "latitude": "",
    "longitude": "",
    "name": "",
    "photo": ""
}
json_template_bd = {
    "latitude": [],
    "longitude": [],
    "name": [],
    "photo": []
}


def get_state_usr(message, action):
    return action[message.chat.id]


def update_state_usr(message, state, action):
    action[message.chat.id] = state


def clean_json(json):
    for name_field in json:
        json[name_field] = ""


def stop_command(message, action):
    btn = ("{}".format(message.text),)
    button = KeyboardBtn(btn)
    bot.send_message(
        chat_id=message.chat.id,
        text='Прерванное действие. Введите еще раз новую команду\n{}'.format(message.text),
        reply_markup=button.create_keyboard()
    )
    if action is USER_STATE_ADD:
        update_state_usr(message, START_CREATE, USER_STATE_ADD)
    elif action is USER_STATE_DEL:
        update_state_usr(message, START_DEL, USER_STATE_DEL)
    elif action is USER_STATE_LIST:
        update_state_usr(message, START_LIST, USER_STATE_LIST)
    clean_json(json_template_currently)


def create_and_del_usr(message):
    bd.set(message.from_user.id, json.dumps(json_template_bd))


def check_not_command(message, action):
    if message.text in commands:
        stop_command(message, action)
        return False
    return True


@bot.message_handler(func=lambda x: True, commands=['start'])
def start_menu(message):
    text = """
    Введите команду:
    1. /add для добавления локации
    2. /list для просмотра 10 последних локаций
    3. /reset для удаления всех локаций
    """
    buttons = KeyboardBtn(commands)
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=buttons.create_keyboard())
    if message.from_user.id not in bd:
        create_and_del_usr(message)


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_ADD) == START_CREATE, commands=['add'])
def start_create(message):
    bot.send_message(chat_id=message.chat.id, text="Отправьте геолокацию")
    update_state_usr(message, GET_LOCATION, USER_STATE_ADD)


@bot.message_handler(
    func=lambda message: get_state_usr(message, USER_STATE_ADD) == GET_LOCATION,
    content_types=["location", "text"]
)
def get_location(message):
    if check_not_command(message, USER_STATE_ADD):
        if message.location is not None:
            json_template_currently["longitude"] = message.location.longitude
            json_template_currently["latitude"] = message.location.latitude
            update_state_usr(message, GET_NAME, USER_STATE_ADD)
            bot.send_message(chat_id=message.chat.id, text="Добавьте имя геолокации")
        elif message.location is None:
            bot.send_message(chat_id=message.chat.id, text="Вы отправили не геолокацию. Попробуйте еще раз.")


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_ADD) == GET_NAME, content_types=["text"])
def get_name(message):
    if check_not_command(message, USER_STATE_ADD):
        if message.text is not None:
            json_template_currently["name"] = message.text
            update_state_usr(message, GET_PHOTO, USER_STATE_ADD)
            text = """
            Добавьте фотографию геолокации или введите любой текст, чтобы не добавлять фотографию
            """
            bot.send_message(chat_id=message.chat.id, text=text)
        elif message.text is None:
            bot.send_message(chat_id=message.chat.id, text="Вы не написали имя локации. Попробуйте еще раз.")


def update_bd(dict, bd, message):
    if message.from_user.id in bd:
        json_from_bd = json.loads(bd.get(message.from_user.id).decode('utf8'))
        for name_field in json_from_bd:
            json_from_bd[name_field].append(dict[name_field])
        bd.set(message.from_user.id, json.dumps(json_from_bd))
    else:
        bd.set(message.from_user.id, json.dumps(dict))


@bot.message_handler(
    func=lambda message: get_state_usr(message, USER_STATE_ADD) == GET_PHOTO,
    content_types=["photo", "text"]
)
def get_photo(message):
    if check_not_command(message, USER_STATE_ADD):
        if message.photo is None:
            json_template_currently["photo"] = NO_PHOTO
        else:
            json_template_currently["photo"] = message.photo[-1].file_id
        bot.send_message(
            chat_id=message.chat.id,
            text="""
            Сохранить? Нажмите на кнопку или ведите да, чтобы сохранить, или любое другое сообщение, чтобы не сохранять
            """,
            reply_markup=yes_no_btns.create_keyboard()
        )
        update_state_usr(message, CONFIRM_ADD, USER_STATE_ADD)


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_ADD) == CONFIRM_ADD, content_types=["text"])
def confirm_add(message):
    if check_not_command(message, USER_STATE_ADD):
        if message.text is not None and message.text.strip().lower() == "да":
            update_bd(json_template_currently, bd, message)
            bot.send_message(chat_id=message.chat.id, text="Локация сохранена.")
        else:
            bot.send_message(chat_id=message.chat.id, text="Локация не сохранена.")
        clean_json(json_template_currently)
        update_state_usr(message, START_CREATE, USER_STATE_ADD)
        bot.send_message(chat_id=message.chat.id, text=BACK_TO_START)


def get_json_loc(message):
    json_loc = json.loads(bd.get(message.from_user.id).decode('utf8'))
    for name_field in json_loc:
        json_template_currently[name_field] = json_loc[name_field]


def get_list_10(json_f, n):
    json_result = {}
    n10 = 10 * n
    for name_field in json_f:
        json_result[name_field] = json_f[name_field][-1 - n10:-11 - n10:-1]
    return json_result


def output_10(message, json10, n):
    right_limit = len(json10["latitude"]) if len(json10["latitude"]) != 10 else 10
    for number in range(right_limit):
        bot.send_message(chat_id=message.chat.id, text="{}. {}".format(n + number + 1, json10["name"][number]))
        bot.send_location(
            chat_id=message.chat.id,
            latitude=json10["latitude"][number],
            longitude=json10["longitude"][number]
        )
        if json10["photo"][number] == NO_PHOTO:
            bot.send_message(chat_id=message.chat.id, text=json10["photo"][number])
        else:
            bot.send_photo(chat_id=message.chat.id, photo=json10["photo"][number])


def output_logic(message, state):
    json10 = get_list_10(json_template_currently, state)
    text_add = ", чтобы добавить введите команду /add"
    len_all_list = len(json_template_currently["latitude"])
    len_json10 = len(json10["latitude"])
    size_n10 = state * 10
    if len_all_list == 0:
        bot.send_message(chat_id=message.chat.id, text="У вас нет геолокаций" + text_add + " . " + BACK_TO_START)
    else:
        if len_all_list < size_n10:
            update_state_usr(message, START_LIST, USER_STATE_LIST)
            bot.send_message(chat_id=message.chat.id, text="Больше нет геолокаций. " + BACK_TO_START)
        else:
            bot.send_message(chat_id=message.chat.id, text="{}/{} :".format(size_n10 + len_json10, len_all_list))
            output_10(message, json10, size_n10)
            button = KeyboardBtn(("Ещё", "Хватит"))
            text1 = "Напишите текст или нажмите кнопку 'Ещё', чтобы дальше смотреть, "
            text2 = "или любой другой текст, чтобы выйти из режима просмотра."
            bot.send_message(chat_id=message.chat.id, text=text1 + text2, reply_markup=button.create_keyboard())
            update_state_usr(message, state + 1, USER_STATE_LIST)


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_LIST) == 0, commands=['list'])
def show_list_first(message):
    get_json_loc(message)
    output_logic(message, get_state_usr(message, USER_STATE_LIST))


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_LIST) > 0)
def show_list(message):
    if check_not_command(message, USER_STATE_LIST):
        if message.text.strip().lower() == "ещё":
            output_logic(message, get_state_usr(message, USER_STATE_LIST))
        else:
            bot.send_message(chat_id=message.chat.id, text=BACK_TO_START)
            clean_json(json_template_currently)
            update_state_usr(message, START_LIST, USER_STATE_LIST)


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_DEL) == START_DEL, commands=['reset'])
def start_reset(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="Удалить? Нажмите на кнопку или ведите да, чтобы удалить, или любое другое сообщение, чтобы не удалять",
        reply_markup=yes_no_btns.create_keyboard()
    )
    update_state_usr(message, CONFIRM_DEL, USER_STATE_DEL)


@bot.message_handler(func=lambda message: get_state_usr(message, USER_STATE_DEL) == CONFIRM_DEL)
def confirm_reset(message):
    if check_not_command(message, USER_STATE_DEL):
        if message.text is not None and message.text.strip().lower() == "да":
            create_and_del_usr(message)
            bot.send_message(chat_id=message.chat.id, text="Все локации удалены. " + BACK_TO_START)
        else:
            bot.send_message(chat_id=message.chat.id, text="Локации не удалены. " + BACK_TO_START)
    update_state_usr(message, START_DEL, USER_STATE_DEL)


if __name__ == '__main__':
  bot.polling(none_stop=True)

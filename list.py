import json
from general_functions import back_to_help, message_btn, clean_json


#sl = START LIST
def command_list_sl(message, bd, json_l, state, start_state, no_ph, bot, btn):
    get_json_loc(message, bd, json_l)
    return output_logic(message, state, start_state, json_l, no_ph, bot, btn)


#nl = NEXT LIST
def command_list_nl(message, state, start_state, json_l, no_ph, bot, btn):
    if message.text.strip().lower() != "ещё":
        clean_json(json_l)
        back_to_help(message, bot)
        return start_state
    return output_logic(message, state, start_state, json_l, no_ph, bot, btn)


def get_json_loc(message, bd, json_l):
    json_loc = json.loads(bd.get(message.from_user.id).decode('utf8'))
    for name_field in json_loc:
        json_l[name_field] = json_loc[name_field]


def output_logic(message, state, start_state, json_l, no_ph, bot, btn):
    json10 = get_list_10(json_l, state)
    text_add = ", чтобы добавить введите команду /add . "
    len_all_list = len(json_l["latitude"])
    len_json10 = len(json10["latitude"])
    if len_all_list < state * 10:
        back_to_help(message, bot, "У вас больше нет геолокаций" + text_add, btn=("/help", "/add"))
        return start_state
    else:
        bot.send_message(chat_id=message.chat.id, text="{} / {}:".format(state * 10 + len_json10, len_all_list))
        output_10_list(message, json10, no_ph, bot, btn, state)
        text1 = "Напишите текст или нажмите кнопку 'Ещё', чтобы дальше смотреть, "
        text2 = "или любой другой текст, чтобы выйти из режима просмотра."
        message_btn(message, text1 + text2, ("Ещё", "Хватит"), bot)
        return state + 1


def get_list_10(json_f, n=0, reverse=True):
    json_result = {}
    n10 = 10 * n
    for name_field in json_f:
        if reverse:
            json_result[name_field] = json_f[name_field][-1 - n10:-11 - n10:-1]
        else:
            json_result[name_field] = json_f[name_field][n10:n10 + 10]
    return json_result


def output_10_list(message, json10, no_ph, bot, btn, n=0):
    right_limit = len(json10["latitude"]) if len(json10["latitude"]) != 10 else 10
    n10 = n * 10
    for number in range(right_limit):
        text = "{}. {}\nЛокация добавленна: {}".format(n10 + number + 1, json10["name"][number], json10["time"][number])
        if json10["photo"][number] == no_ph:
            bot.send_message(chat_id=message.chat.id, text=text + "\n" + json10["photo"][number])
        else:
            bot.send_photo(chat_id=message.chat.id, photo=json10["photo"][number], caption=text)
        bot.send_location(
            chat_id=message.chat.id,
            latitude=json10["latitude"][number],
            longitude=json10["longitude"][number],
            reply_markup=btn.create_keyboard(json10["latitude"][number], json10["longitude"][number],
            json10["name"][number])
        )

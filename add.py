import datetime
from general_functions import message_btn, update_bd, back_to_help, clean_json


#sc = START CREATE
def command_add_sc(message, bot):
    bot.send_message(chat_id=message.chat.id, text="Отправьте геолокацию")


#gl = GET LOCATION
def command_add_gl(message, json_v, bot):
    text = "Вы отправили не геолокацию. Попробуйте еще раз."
    go_next = False
    if message.location is not None:
        json_v["longitude"] = message.location.longitude
        json_v["latitude"] = message.location.latitude
        json_v["time"] = datetime.datetime.now().strftime("%H:%M %d/%m/%y")
        text = "Добавьте имя геолокации"
        go_next = True
    bot.send_message(chat_id=message.chat.id, text=text)
    return go_next


#gn = GET NAME
def command_add_gn(message, json_v, bot, no_ph):
    json_v["name"] = message.text
    text = """
    Добавьте фотографию геолокации или введите любой текст, чтобы не добавлять фотографию
    """
    message_btn(message, text, (no_ph,), bot)


#gp = GET PHOTO
def command_add_gp(message, json_v, no_ph, yes_no, bot):
    if message.photo is None:
        json_v["photo"] = no_ph
    else:
        json_v["photo"] = message.photo[-1].file_id
    text = """
    Сохранить? Нажмите на кнопку или ведите да, чтобы сохранить, или любое другое сообщение, чтобы не сохранять
    """
    message_btn(message, text, yes_no, bot)


#ca = CONFIRM ADD
def command_add_ca(message, json_v, bd, bot):
    text = "Локация не сохранена. "
    if message.text is not None and message.text.strip().lower() == "да":
        update_bd(json_v, bd, message)
        text = "Локация сохранена. "
    clean_json(json_v)
    back_to_help(message, bot, text)

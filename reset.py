from general_functions import message_btn, create_and_del_usr, back_to_help


#sd = START DEL
def command_list_sd(message, bot, btn):
    text = "Удалить? Нажмите на кнопку или ведите да, чтобы удалить, или любое другое сообщение, чтобы не удалять"
    message_btn(message, text, btn, bot)


#cd = CONFIRM DEL
def command_list_cd(message, bd, json_d, bot):
    text = "Локации не удалены. "
    if message.text is not None and message.text.strip().lower() == "да":
        create_and_del_usr(message, bd, json_d)
        text = "Все локации удалены. "
    back_to_help(message, bot, text)

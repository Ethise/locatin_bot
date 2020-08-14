from general_functions import message_btn


def command_help(message, bot):
    text1 = "Введите команду:\n1. /add для добавления локации\n2. /list для просмотра 10 последних локаций\n"
    text2 = "3. /reset для удаления всех локаций"
    message_btn(message, text1 + text2, ("/add", "/list", "/reset"), bot)

from abc import ABC, abstractmethod
from telebot import types
from google_maps_api import output_interest


class AbstractButton(ABC):

    @abstractmethod
    def create_keyboard(self):
        pass


class InlineKeyboardBtn(AbstractButton):

    @abstractmethod
    def create_keyboard(self, *args):
        pass

    @abstractmethod
    def callback(self, callback_query):
        pass


class KeyboardBtn(AbstractButton):

    def __init__(self, text_btns):
        self.text_btns = text_btns

    def create_keyboard(self):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btns = [types.KeyboardButton(text_btn) for text_btn in self.text_btns]
        markup.add(*btns)
        return markup


class NearbyPlaces(InlineKeyboardBtn):

    def __init__(self, type, bot):
        self.type = str(type)
        self.bot = bot

    def create_keyboard(self, lat_place, lng_place, name_place):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button = types.InlineKeyboardButton(
            text="Места поблизости",
            callback_data=self.type + "^" + str(lat_place) + "^" + str(lng_place) + "^" + name_place
        )
        keyboard.add(button)
        return keyboard

    def callback(self, callback_query):
        message = callback_query.message
        lat, lng, name = callback_query.data.split("^")[1:4]
        self.bot.send_message(chat_id=message.chat.id, text="Места поблизости '{}'".format(name))
        output_interest(message, lat, lng, self.bot)
        text1 = "Напишите текст или нажмите кнопку 'Ещё', чтобы дальше смотреть, "
        text2 = "или любой другой текст, чтобы выйти из режима просмотра."
        self.bot.send_message(chat_id=message.chat.id, text=text1 + text2)
        return message

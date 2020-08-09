from abc import ABC, abstractmethod
from telebot import types


class AbstractButton(ABC):

    @abstractmethod
    def create_keyboard(self):
        pass


class InlineKeyboardBtn(AbstractButton):

    @abstractmethod
    def create_keyboard(self):
        pass

    @abstractmethod
    def callback(self):
        pass


class KeyboardBtn(AbstractButton):

    def __init__(self, text_btns):
        self.text_btns = text_btns

    def create_keyboard(self):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btns = [types.KeyboardButton(text_btn) for text_btn in self.text_btns]
        markup.add(*btns)
        return markup
